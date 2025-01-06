"""
encoding-decoding tests
"""
import sys, os, glob
from dataEncoder import encode, decode
import shutil

#decode('out', 'decout')    
#sys.exit()
    
datasetPth='/home/hackassen/works/dataEncoder/x-ray_dataset'
outputPth="out"
objectPth="payloads/4. Array’s Operators.srt"

# clearing output directory
for file in glob.glob(os.path.join(outputPth, '*')):    
    if os.path.isfile(file):
            os.remove(file)
    elif os.path.isdir(file):
        shutil.rmtree(file)
                        
encode(objectPth, datasetPth, outputPth)
print("all done")



