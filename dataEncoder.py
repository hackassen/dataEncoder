#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
data encoder test
"""

from PIL import Image
import numpy as np
from pathlib import Path
import os, pdb, re, sys
import json, hashlib
from tqdm import tqdm
from glob import iglob

from matplotlib import pyplot as plt
#import glob

METAFILE='meta.txt'
DEBUG=True
IMG_DATASET_TYPES=[".jpeg", ".jpg", ".png"]

def get_sha256_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

#here coul be better to use the  glob.iglob
#def dir_traverse(directory:str, filter_types:list, results:list, verb=False):
#    for fl in os.listdir(directory):
#        fl_path = os.path.join(directory, fl)
#        if os.path.isdir(fl_path):
##            #print("     - DIR")
#            dir_traverse(fl_path, filter_types, results)
#        elif os.path.isfile(fl_path) and os.path.splitext(fl)[-1] in filter_types:
#            if verb: print(f"   {fl}")
#            results.append(fl_path)
def dir_traverse(directory:str, filter_types:list):
    #fls=[]
    for type_ in filter_types: 
        for fl in iglob(f"**/*{type_}", root_dir=directory, recursive=True):
            yield fl
        #fls.extend(list(iglob(f"**/*{type_}", root_dir=directory, recursive=True)))
    #return fls
    

def encode_to_imageset(fileToEncode, maskingDatasetPth, outputPth):
    file=Path(fileToEncode)
    #images=[]
    #dir_traverse(maskingDatasetPth, IMG_DATASET_TYPES, images)
    #for type_ in IMG_DATASET_TYPES: 
    #    images.extend(list(iglob(f"**/*{type_}", root_dir=maskingDatasetPth, recursive=True)))
    
    #pdb.set_trace()
    output=Path(outputPth)
    assert file.exists()
    #assert len(images)
    os.makedirs(output, exist_ok=True)
    original_sha=get_sha256_hash(file)
    print("   > original sha: ",original_sha)
    meta={
        'sha': original_sha,
        'name': file.name
        }
    object_size=os.path.getsize(file)
    print("    size of the file been encoded %i "%object_size)
    
    tail=0
    dataend_flag=0
    with open(file, 'rb') as data_hendler:
            order_mark=0
            total_bytes=0
            total_images=0
            while True: #                       # dataset loop
                for i, impth in enumerate(tqdm(dir_traverse(maskingDatasetPth, IMG_DATASET_TYPES), desc="images encoded: ")): #=======       image loop =============                    
                    
                    impth=Path(impth)
                    #print(f"    - {impth} processing....")
                    image=np.array(Image.open(Path(maskingDatasetPth) / impth).convert("RGB"))
                    #pdb.set_trace()
                    
                    image_lth=image[:,:,0].size                    
                    data_ch=np.frombuffer(
                        data_hendler.read(image_lth), 
                        dtype=np.uint8)
                    
                    if not data_ch.size: 
                        print("   the end of object happened.")
                        dataend_flag=1
                        break                   #       exit the image loop
                    tail=image_lth-len(data_ch) 
                    total_images+=1
                    total_bytes+=len(data_ch)
                    
                    if tail: 
                        print(" got tail :", tail)
                        data_ch=np.concatenate([data_ch, np.ones(tail)])
                        meta['last_image']=total_images
                        
                    image[:,:,2]=data_ch.reshape(image.shape[:2])
                                                          
                    save_dir=output/impth.parent
                    #pdb.set_trace()
                    if not save_dir.exists(): os.makedirs(save_dir)
                    #Image.fromarray(image).save(save_dir.as_posix()+"/"+impth.stem+"_"+str(order_mark)+impth.suffix)
                    Image.fromarray(image).save(save_dir.as_posix()+"/"+impth.stem+"_"+str(order_mark)+".png")
                    order_mark+=1
                     
                if dataend_flag: break #                exit the dataset loop
                
            print("Data encoding ends, overall processed %i images. "%total_images)
            meta['tail']=tail
            metaPth=output/Path(METAFILE)
            with open(metaPth, 'w') as h:            
                json.dump(meta, h)
            print("    %i bytes been wrote. "%total_bytes)
            print("The metafile has been writed to %s" % metaPth.as_posix())
            

def decode(encPth, outPth):
    encPth=Path(encPth)
    output=Path(outPth)
    assert encPth.exists()
    metaPth=encPth/Path(METAFILE)
    assert metaPth.exists()
    os.makedirs(outPth, exist_ok=True)
    with open(metaPth, 'r') as h:        
        meta=json.load(h)
    print("Found the metafile. ")
    sha, name, tail, last_image=meta['sha'], meta['name'], meta['tail'], meta['last_image']
    print("    recovering file '%s'"%name)    
    #videos=list()
    #dir_traverse(encPth,"*.mp4", videos)
    im_list=list(dir_traverse(encPth, IMG_DATASET_TYPES))
    with open(output/Path(name), 'wb') as data_h:
        im_order_list=[int(re.search("(\d+)\.[\d\w]{3,4}$", v)[1]) for v in im_list]
        #pdb.set_trace()
        im_list=np.array(im_list)[np.argsort(im_order_list)]
        #pdb.set_trace()
        total_bytes=0    
        total_images=0
        for imFl in im_list:
            print("    '%s' processing ..."%imFl)
            im=np.array(Image.open(encPth/Path(imFl)).convert("RGB"))            
            data_ch=im[:,:,2].reshape(-1)            
            
            #print("    >  %i bytes processed.."%total_bytes)
            if imFl==im_list[-1]:                                             # clipping the tail
                print("    clipping %i bytes of tail"%tail, " on the %i -th image"%total_images)
                #pdb.set_trace()
                data_ch=data_ch[:-tail]
            total_bytes+=data_ch.size
            #pdb.set_trace()
            data_h.write(data_ch.tobytes())
            total_images+=1
            #pdb.set_trace()                
            print("    Writed down %i bytes of data"%total_bytes)
        print("    total_images: %i"%total_images)
        
    result_sha=get_sha256_hash(output/Path(name))    
    if sha!=result_sha: sys.exit(" initial and result shas doesn't match.")
    
                #
                
                
if __name__=="__main__":
    decode('out', 'decout')    
    sys.exit()
        
    datasetPth='/home/hackassen/works/dataEncoder/x-ray_dataset'
    outputPth="out"
    objectPth="drive.tar.gz"
    encode_to_imageset(objectPth, datasetPth, outputPth)
    print("all done")
