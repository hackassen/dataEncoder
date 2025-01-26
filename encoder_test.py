"""
encoding-decoding tests
"""
import sys, os, glob
from dataEncoder import encode, decode
import shutil
    
#datasetPth='/home/hackassen/works/dataEncoder/x-ray_dataset'
datasetPth='/home/hackassen/Downloads/movies/[Udemy] Python Programming Machine Learning, Deep Learning (05.2021)/'

outputPth="out"
objectPth="payloads/4. Array’s Operators.srt"
#objectPth="payloads/Be Svendsen - Circle (Mollono.Bass Remix).mp3.tar.gz"

# clearing output directory
for file in glob.glob(os.path.join(outputPth, '*')):    
    if os.path.isfile(file):
            os.remove(file)
    elif os.path.isdir(file):
        shutil.rmtree(file)
                        
encode(objectPth, datasetPth, outputPth)
print("all done")



