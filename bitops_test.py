"""
bitwise operations test
"""

from utils import  print_byte, replaceLSB, iterByte  

t=0b10110011

print("="*20, "\ninitial byte: \n", print_byte(t))

lsbs=[1,2,4,8]
for lsb in lsbs:
    print('LSB: ', lsb)
    print("iteration.")    
    for bt in iterByte(t, lsb):
        print("    ", print_byte(bt))

    print("replacing.")    
    print("    ", print_byte(replaceLSB(t, 0b11111111, lsb)))


