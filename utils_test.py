"""
some of the utils test
"""

from utils import  print_byte, replaceLSB, print_arrBytewise, extractLSB
import numpy as np

frame=np.random.randint(0,255, 2).astype(np.uint8) 

LSBitsN=2

print("-"*10,"\noriginal frame:") 
print_arrBytewise(frame)

data=np.array([
      0b01000001,
      0b00101010,
      #0b00000010,
      #0b00000001,
      ], dtype=np.uint8)

print("-"*10,"\npayload: \n")
#print(data, "\n", "-"*4)
print_arrBytewise(data)

new_frames=replaceLSB(frame, data, LSBitsN)
print("-"*10,"\nnew frames: ")
for pix_i in range(new_frames.shape[0]):
    print("    pixel#", pix_i)
    for shift_i in range(new_frames.shape[1]):
        print("        ", print_byte(new_frames[pix_i, shift_i]))

rec=extractLSB(new_frames, LSBitsN)
print("="*10,"\nrec data: \n", rec)
print_arrBytewise(rec)
assert (rec-data).sum()==0
print("passed")
#print((print_byte(rec)))
