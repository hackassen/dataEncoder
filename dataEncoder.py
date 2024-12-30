#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
data encoder test
"""

from PIL import Image
import numpy as np
from pathlib import Path
import os, pdb, re, sys
import json
from tqdm import tqdm
#from glob import iglob

from matplotlib import pyplot as plt

from utils import dir_traverse, get_sha256_hash, replaceLSB, extractLSB  

METAFILE='meta.txt'
DEBUG=True
IMG_DATASET_TYPES=[".jpeg", ".jpg", ".png"]

LSBits_AVALIBLE=[1, 2, 4, 8]

def encode_to_imageset(fileToEncode, maskingDatasetPth, outputPth, LSBits=2):
    assert LSBits in LSBits_AVALIBLE
    
    file=Path(fileToEncode)    
    output=Path(outputPth)
    assert file.exists()
    os.makedirs(output, exist_ok=True)
    original_sha=get_sha256_hash(file)
    print("   > original sha: ",original_sha)
    meta={
        'sha': original_sha,
        'name': file.name,
        'LSBits':LSBits,
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
                    image=np.array(Image.open(Path(maskingDatasetPth) / impth).convert("RGB"))
                    image_lth=image[:,:,0].size                    
                    data_ch=np.frombuffer(
                        data_hendler.read(image_lth), 
                        dtype=np.uint8)
                    
                    if not data_ch.size: 
                        print("   the end of object happened.")
                        dataend_flag=1
                        break                   #       exit the image loop
                    tail=image_lth-len(data_ch) 
                    #total_images+=1
                    total_bytes+=len(data_ch)
                    
                    if tail: 
                        print(" got tail :", tail)
                        data_ch=np.concatenate([data_ch, np.ones(tail, dtype=np.uint8)])
                        #meta['last_image']=total_images
                        
                    save_dir=output/impth.parent
                    #pdb.set_trace()
                    if not save_dir.exists(): os.makedirs(save_dir)
                    blue_chan=image[:,:,2].reshape(-1)
                    payload=data_ch; #data_ch.reshape(image.shape[:2])
                    encoded_blue_chan=replaceLSB(blue_chan, payload, LSBits)
                    #pdb.set_trace()
                    for shift_i in range(encoded_blue_chan.shape[1]):  
                        image[:,:,2]=encoded_blue_chan[:, shift_i].reshape(image.shape[:2])
                        Image.fromarray(image).save(save_dir.as_posix()+"/"+impth.stem+"_"+str(order_mark)+".png")
                        order_mark+=1
                        total_images+=1

                if dataend_flag: break #                exit the dataset loop
                
            print("Data encoding ends, overall processed %i images. "%total_images)
            meta['tail']=tail
            meta['last_image']=total_images
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
    sha, name, tail, last_image, LSBits=meta['sha'], meta['name'], meta['tail'], meta['last_image'], meta['LSBits']
    LSBshiftsN=int(8/LSBits)
    assert last_image%LSBshiftsN==0
    
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
        im_shifts_batch=[]
        for imFl in im_list:
            print("    '%s' processing ..."%imFl)
            im=np.array(Image.open(encPth/Path(imFl)).convert("RGB"), dtype=np.uint8)            
            data_ch=im[:,:,2].reshape(-1)
                        
            #print("    >  %i bytes processed.."%total_bytes)
            if total_images>=last_image-LSBshiftsN:                                             # clipping the tail
                print("    clipping %i bytes of tail"%tail, " on the %i -th image"%total_images)
                #pdb.set_trace()
                data_ch=data_ch[:-tail]
            total_bytes+=data_ch.size
            total_images+=1
            
            im_shifts_batch.append(data_ch)
            if(len(im_shifts_batch)==LSBshiftsN):
                decoded_data=extractLSB(np.array(im_shifts_batch).T, LSBits)
                data_h.write(decoded_data.tobytes())                
                im_shifts_batch=[]
            #pdb.set_trace()                
            print("    Writed down %i bytes of data"%total_bytes)
        print("    total_images: %i"%total_images)
        
    result_sha=get_sha256_hash(output/Path(name))    
    if sha!=result_sha: sys.exit(" initial and result shas doesn't match.")
    
                
if __name__=="__main__":
    sys.exit("No unit tests avalible.")
    