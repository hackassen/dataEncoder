#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
data encoder test
"""

from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio import *
from moviepy.editor import concatenate_videoclips, ImageSequenceClip
from moviepy.audio.AudioClip import concatenate_audioclips

import numpy as np
from pathlib import Path
import os, pdb, re, sys
import json, hashlib
from tqdm import tqdm

from matplotlib import pyplot as plt

METAFILE='meta.txt'
DEBUG=True

def get_sha256_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def dir_traverse(directory:str, filter_types:list, results:list, verb=False):
    for fl in os.listdir(directory):
        fl_path = os.path.join(directory, fl)
        if os.path.isdir(fl_path):
            #print("     - DIR")
            dir_traverse(fl_path, filter_types, results)
        elif os.path.isfile(fl_path) and os.path.splitext(fl)[-1] in filter_types:
            if verb: print(f"   {fl}")
            results.append(fl_path)

def encode(fileToEncode, maskingVideoPth, outputPth):
    file=Path(fileToEncode)
    video=Path(maskingVideoPth)
    output=Path(outputPth)
    assert file.exists()
    assert video.exists()
    os.makedirs(output, exist_ok=True)
    meta={
        'sha': get_sha256_hash(file),
        'name': file.name
        }
    print("    size of the file been encoded %i "%os.path.getsize(file))
    #!tp
    sha256_hash=hashlib.sha256()
    tp_sha=hashlib.sha256()
    sha2=hashlib.sha256()
    
    videos=list()
    dir_traverse(video,"*.mp4", videos)
    if not len(videos): raise Exception("no '*.mp4' files found in maskingVideoPth. (Currently only '.mp4' files supported)")
    tail=0
    dataend_flag=0
    with open(file, 'rb') as data_hendler:
            clip_id=0
            total_bytes=0
            total_frames=0
            for videoPth in videos: #=======       video loop =============                
                clip_id+=1
                clip = VideoFileClip(videoPth)
                fps=clip.fps
                #pdb.set_trace()
                
                encoded_frames=list()
                for i, frame in enumerate(clip.iter_frames()): #=======       frame loop =============                    
                    
                    #pdb.set_trace()
                    #plt.imshow(frame)
                    #plt.waitforbuttonpress()
                    frame_lth=frame[:,:,0].size                    
                    data_ch=data_hendler.read(frame_lth)
                    #pdb.set_trace() 
                    data_ch=np.frombuffer(data_ch, dtype=np.uint8)
                    
                    #!tp 
                    sha0=hashlib.sha256(); sha0.update(data_ch.tobytes()); print("sha0:", sha0.hexdigest())
                    ch0=data_ch
                    
                    if not data_ch.size: 
                        print("   the end of object happened.")
                        dataend_flag=1
                        break                   #       exit the frame loop
                    total_frames+=1
                    tail=frame_lth-len(data_ch) 

                    if tail: 
                        print(" got tail :", tail)
                        #tp_data=
                        #pdb.set_trace()
                        #!tp                        
                        sha256_hash.update(np.concatenate([np.array(encoded_frames)[:,:,:,2].reshape(-1), data_ch ]).tobytes())                        
                        print("frames : ", sha256_hash.hexdigest())
                        print("initial:", meta['sha'])
                        print("bytes  :", tp_sha.hexdigest())
                        
                        #sys.exit()
                        
                        
                        data_ch=np.concatenate([data_ch, np.ones(tail)])
                        meta['last_frame']=total_frames
                    newFrame=frame.copy()
                    newFrame[:,:,2]=data_ch.reshape(frame.shape[:2])
                                        
                    encoded_frames.append(newFrame)
                    
                    dataend_flag=1
                    break
                                
                    #sha256_hash.update(np.array(encoded_frames)[:,:,:,2].reshape(-1).tobytes())                        
                    #print("frames : ", sha256_hash.hexdigest())
                    #print("bytes  :", tp_sha.hexdigest())
                    #pdb.set_trace() 
                    
                    total_bytes+=data_ch.size
                    #plt.imshow(newFrame)
                #pdb.set_trace()
                
                #saving collected list of frames to clip
                
                newClip=ImageSequenceClip(encoded_frames, fps=fps)
                
                
                videoPth=Path(videoPth)
                newClip.write_videofile(
                    output.as_posix()+"/"+videoPth.stem+"_"+str(clip_id)+videoPth.suffix, 
                    ffmpeg_params={'-crf': '0'},
                    preset='veryfast', #'veryslow'
                    )
                if dataend_flag: break #                exit the clip loop
                
            print("Data encoding ends, overall processed %i frames. "%total_frames)
            meta['tail']=tail
            metaPth=output/Path(METAFILE)
            with open(metaPth, 'w') as h:            
                json.dump(meta, h)
            print("    %i bytes been wrote. "%total_bytes)
            print("The metafile has been writed to %s" % metaPth.as_posix())
            

    #!tp 2
    ch2=np.array(encoded_frames)[:, :,:,2].reshape(-1)
    sha2.update(ch2.tobytes()); print("sha2:", sha2.hexdigest())

    
    #tp
    clip = VideoFileClip(output.as_posix()+"/"+videoPth.stem+"_"+str(clip_id)+videoPth.suffix, audio=False)
    frames=np.array(list(clip.iter_frames()))[:,:,:,2].reshape(-1)
    sha3=hashlib.sha256(); sha3.update(frames.tobytes()); print("sha3:", sha3.hexdigest())

    #pdb.set_trace()
    #pdb.set_trace()
    

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
    sha, name, tail, last_frame=meta['sha'], meta['name'], meta['tail'], meta['last_frame']
    print("    recovering file '%s'"%name)    
    videos=list()
    dir_traverse(encPth,"*.mp4", videos)
    with open(output/Path(name), 'wb') as data_h:
        video_order_list=[int(re.search("(\d+)\.mp4$", v)[1]) for v in videos]
        videos=np.array(videos)[np.argsort(video_order_list)]
        total_bytes=0    
        total_frames=0
        for videoFl in videos:
            print("    '%s' processing ..."%videoFl)
            clip = VideoFileClip(videoFl, audio=False)
            
            #framesN=int(clip.fps*clip.duration)
            
            for i, frame in enumerate(tqdm(clip.iter_frames(), desc="frames processed..")): # may be need to define fps here....
                total_frames+=1
                #pdb.set_trace()                
                data_ch=frame[:,:,2].reshape(-1)
                #print("    >  %i bytes processed.."%total_bytes)
            
                if videoFl==videos[-1] and i+1==last_frame:                                             # clipping the tail
                    print("    clipping %i bytes of tail"%tail, " on the %i -th frame"%total_frames)
                    #pdb.set_trace()
                    data_ch=data_ch[:-tail]
                total_bytes+=data_ch.size
                pdb.set_trace()
                data_h.write(data_ch.tobytes())
            print("    Writed down %i bytes of data"%total_bytes)
        print("    total_frames: %i"%total_frames)
        
    result_sha=get_sha256_hash(output/Path(name))    
    if sha!=result_sha: sys.exit(" initial and result shas doesn't match.")
    
                #
                
                
if __name__=="__main__":
    #decode('out', 'decout')    
    #sys.exit()
    
    
    videoCarrierPth='/home/hackassen/Downloads/movies/[Udemy] Python Programming Machine Learning, Deep Learning (05.2021)/'
    outputPth="out"
    objectPth="Be Svendsen - Circle (Mollono.Bass Remix).mp3"
    encode(objectPth, videoCarrierPth, outputPth)
    print("all done")
