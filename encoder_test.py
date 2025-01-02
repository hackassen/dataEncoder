"""
encoding-decoding tests
"""
import sys, os, glob
from dataEncoder import encode_to_imageset, decode
import shutil

#decode('out', 'decout')    
#sys.exit()
    
datasetPth='/home/hackassen/works/dataEncoder/x-ray_dataset'
outputPth="out"
objectPth="payloads/Be Svendsen - Circle (Mollono.Bass Remix).mp3.tar.gz"

# clearing output directory
for file in glob.glob(os.path.join(outputPth, '*')):    
    if os.path.isfile(file):
            os.remove(file)
    elif os.path.isdir(file):
        #os.rmdir(file)
        shutil.rmtree(file)
                        
encode_to_imageset(objectPth, datasetPth, outputPth)
print("all done")



