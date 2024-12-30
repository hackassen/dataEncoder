"""
encoding-decoding tests
"""
import sys, os, glob
from dataEncoder import encode_to_imageset, decode

#decode('out', 'decout')    
#sys.exit()
    
datasetPth='/home/hackassen/works/dataEncoder/x-ray_dataset'
outputPth="out"
objectPth="payloads/LASCALA - Пульс.mp3"

# clearing output directory
for file in glob.glob(os.path.join(outputPth, '*')):    
    if os.path.isfile(file):
            os.remove(file)
    elif os.path.isdir(file):
        os.rmdir(file)
                        
encode_to_imageset(objectPth, datasetPth, outputPth)
print("all done")



