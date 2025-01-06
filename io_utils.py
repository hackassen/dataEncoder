"""
image frames for encoding input/output utils
"""

from PIL import Image
import numpy as np
from pathlib import Path
import os, pdb, re, sys
from utils import dir_traverse
from glob import iglob

IMG_DATASET_TYPES=[".jpeg", ".jpg", ".png"]
VIDEO_DATASET_TYPES=[".mp4",]
#SUFFIXES_AVALIBLE=[""]

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
    def iter_forever(video_path):
        pass

class imset_writer():
    def __init__(self, save_dir, suffix='.png'):
        self.order_mark=0
        self.save_dir=Path(save_dir)
        if not self.save_dir.exists(): os.makedirs(self.save_dir)
        self.suffix=suffix
    
    def write(self, im, ID):
        Image.fromarray(im).save(self.save_dir.as_posix()+"/"+ID+"_"+str(self.order_mark)+self.suffix)
        self.order_mark+=1

class video_writer():
    def __init__(self, save_dir):
        pass        
    def write(self, im, name,  pardir):
        pass
    
def infer_io(path):
    '''
    infer image provider and writer by path
    '''
    for video_type in VIDEO_DATASET_TYPES:
        if len(list(iglob("**/*"+video_type, root_dir=path, recursive=True))): return video_provider, video_writer

    for im_type in IMG_DATASET_TYPES:
        if len(list(iglob("**/*"+im_type, root_dir=path, recursive=True))): return imset_provider, imset_writer
        
    raise Exception("   !ERROR:infer_provider: wrong 'path'")