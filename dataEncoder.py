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
from matplotlib import pyplot as plt

from utils import dir_traverse, get_sha256_hash, replaceLSB, extractLSB, timeit
from io_utils import infer_io

METAFILE='meta.txt'
DEBUG=True
LSBits_AVALIBLE=[1, 2, 4, 8]
 
@timeit
def encode(fileToEncode, maskingPth, outputPth, LSBits=2):
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
    print("    size of the file been encoded %i bytes"%object_size)
    provider_type, writer_type=infer_io(maskingPth)
    provider=provider_type(maskingPth)
    writer=writer_type(outputPth)
    
    tail=0
    #dataend_flag=0
    with open(file, 'rb') as data_hendler:
            order_mark=0
            total_bytes=0
            total_images=0
            
            for i, (imID, image) in enumerate(tqdm(provider.iter(), desc="images encoded: ")): #=======       image loop =============                                    
                image_lth=image[:,:,0].size                    
                data_ch=np.frombuffer(
                    data_hendler.read(image_lth), 
                    dtype=np.uint8)
                
                if not data_ch.size: 
                    print("   the end of object happened.")
                    #dataend_flag=1
                    break                   #       exit the image loop
                tail=image_lth-len(data_ch) 
                #total_images+=1
                total_bytes+=len(data_ch)
                
                if tail: 
                    print(" got tail :", tail)
                    data_ch=np.concatenate([data_ch, np.ones(tail, dtype=np.uint8)])
                    #meta['last_image']=total_images
                    
                blue_chan=image[:,:,2].reshape(-1)
                payload=data_ch; #data_ch.reshape(image.shape[:2])
                encoded_blue_chan=replaceLSB(blue_chan, payload, LSBits)
                for shift_i in range(encoded_blue_chan.shape[1]):  
                    image[:,:,2]=encoded_blue_chan[:, shift_i].reshape(image.shape[:2])
                    writer.write(image, imID)
                    order_mark+=1
                    total_images+=1
                print("    processed {:.2f}/{:.2f} Mb".format(total_bytes/1E+6, object_size/1E+6))
                
                #if dataend_flag: break #                exit the dataset loop            
            
            print("Data encoding ends, overall processed %i images. "%total_images)
            meta['tail']=tail
            meta['last_image']=total_images
            metaPth=output/Path(METAFILE)
            with open(metaPth, 'w') as h:            
                json.dump(meta, h)
            print("    %i bytes been wrote. "%total_bytes)
            print("The metafile has been writed to %s" % metaPth.as_posix())

@timeit        
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
    provider_type, writer_type=infer_io(encPth)
    provider=provider_type(encPth)

    with open(output/Path(name), 'wb') as data_h:
        total_bytes=0    
        total_images=0
        im_shifts_batch=[]
        #for imFl in im_list:
        for imID, im in provider.iter(forever=False):
            print("    '%s' processing ..."%imID)
            data_ch=im[:,:,2].reshape(-1)
                        
            #print("    >  %i bytes processed.."%total_bytes)
            if total_images>=last_image-LSBshiftsN:                                             # clipping the tail
                print("    clipping %i bytes of tail"%tail, " on the %i -th image"%total_images)
                data_ch=data_ch[:-tail]
            total_images+=1
            
            im_shifts_batch.append(data_ch)
            if(len(im_shifts_batch)==LSBshiftsN):
                decoded_data=extractLSB(np.array(im_shifts_batch).T, LSBits)
                data_h.write(decoded_data.tobytes())                
                total_bytes+=decoded_data.size
                im_shifts_batch=[]
                print("    Writed down %i bytes of data"%total_bytes)
            #pdb.set_trace()                
        print("    total_images: %i"%total_images)
        
    result_sha=get_sha256_hash(output/Path(name))    
    if sha!=result_sha: sys.exit(" initial and result shas doesn't match.")

                
if __name__=="__main__":
    sys.exit("No unit tests avalible.")
    