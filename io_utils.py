"""
image frames for encoding input/output utils
"""

from PIL import Image
import numpy as np
from pathlib import Path
import os, pdb, re, sys
from utils import dir_traverse
from glob import iglob
import cv2

IMG_DATASET_TYPES=[".jpeg", ".jpg", ".png"]
VIDEO_DATASET_TYPES=[".mp4", ".avi"]
#SUFFIXES_AVALIBLE=[""]
FPS=24

class imset_provider:
    def __init__(self, imset_path):
        self.imset_path=imset_path
        self.order=0
        
    def iter(self, forever=True):
        im_list=list(dir_traverse(self.imset_path, IMG_DATASET_TYPES))
        try:
            im_order_list=[int(re.search("_(\d+)\.[\d\w]{3,4}$", v)[1]) for v in im_list]
            im_list=np.array(im_list)[np.argsort(im_order_list)]
            print("    Note! found ordered imageset")
        except:
            print("    Note! imageset is not ordered")
        while True:
            for pth in im_list:
                pth=Path(pth)
                image=np.array(Image.open(Path(self.imset_path) / pth).convert("RGB"), dtype=np.uint8)
                ID="i"+str(hash(pth))
                self.order+=1
                yield ID, image
            if not forever: break
 
class video_provider():
    def __init__(self, video_path):
        self.video_path=video_path
        self.order=0
        
    def iter(self, forever=True):
        video_list=list(dir_traverse(self.video_path, VIDEO_DATASET_TYPES))
        try:
            video_order_list=[int(re.search("_(\d+)\.[\d\w]{3,4}$", v)[1]) for v in video_list]
            video_list=np.array(video_list)[np.argsort(video_order_list)]
            print("    Note! found ordered videoset")
        except:
            print("    Note! videoset is not ordered")
        frame=None
        while True:
            for pth in video_list:
                pth= Path(self.video_path) / Path(pth)
                print(f"    '{pth.as_posix()}' - processsing...")
                cap=cv2.VideoCapture(pth)
                
                #!!tp
                frameNo=0
                maxFrames=5
                
                while cap.isOpened():
                    ret, frame=cap.read()
                    if not ret: break            
                    image=np.array(frame, dtype=np.uint8)
                    ID="i"+str(hash(pth))
                    
                    #!!tp
                    frameNo+=1
                    if frameNo==maxFrames: break
                    
                    yield ID, image
                cap.release()
                self.order+=1
                if frame is None: break; #raise Exception(f" invalud video: '{pth.as_posix()}'")
            if not forever: break

class imset_writer():
    def __init__(self, save_dir, suffix='.png'):
        self.order_mark=0
        self.save_dir=Path(save_dir)
        if not self.save_dir.exists(): os.makedirs(self.save_dir)
        self.suffix=suffix
    
    def write(self, im, ID, suffix='.png'):
        Image.fromarray(im).save(self.save_dir.as_posix()+"/"+ID+"_"+str(self.order_mark)+self.suffix)
        self.order_mark+=1

class video_writer():
    def __init__(self, save_dir):
        self.order_mark=0
        self.flID=None
        self.save_dir=Path(save_dir)
        if not self.save_dir.exists(): os.makedirs(self.save_dir)
        self.codec=cv2.VideoWriter_fourcc(*'IYUV')
        self.writer=None

    def write(self, frame, flID):
        if not self.flID==flID: # switch to next videofile
            if not self.writer is None: self.writer.release()
            flPth=self.save_dir/Path(flID+"_"+str(self.order_mark)+".avi")
            print(f"   ++ writing to '{flPth}'")
            h,w,_=frame.shape
            self.writer=cv2.VideoWriter(flPth, self.codec, FPS, (w,h))
            #pdb.set_trace()
            self.flID=flID
            self.order_mark+=1
        #pdb.set_trace()                    
        self.writer.write(frame)
            
    
def infer_io(path):
    '''
    infer image provider and writer by path
    '''
    for video_type in VIDEO_DATASET_TYPES:
        if len(list(iglob("**/*"+video_type, root_dir=path, recursive=True))): return video_provider, video_writer

    for im_type in IMG_DATASET_TYPES:
        if len(list(iglob("**/*"+im_type, root_dir=path, recursive=True))): return imset_provider, imset_writer
        
    raise Exception("   !ERROR:infer_provider: wrong 'path'")