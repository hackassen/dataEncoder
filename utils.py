
from glob import iglob
import hashlib
import numpy as np
import pdb
from copy import deepcopy
import time

def get_sha256_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def dir_traverse(directory:str, filter_types:list):
    for type_ in filter_types: 
        for fl in iglob(f"**/*{type_}", root_dir=directory, recursive=True):
            yield fl
            
LSB_PATTERNS={
    1:[0b11111110, 0b1],
    2:[0b11111100, 0b11],
    4:[0b11110000, 0b1111],
    8:[0b00000000, 0b11111111],
    }

#def replaceLSB(byte_, new_bits, LSBits):
#    return (byte_ & LSB_PATTERNS[LSBits][0]) | (new_bits & LSB_PATTERNS[LSBits][1])

#def iterByte(byte_, LSBits):
#    for shift in range(0, int(8), LSBits):        
#        yield byte_>>shift&LSB_PATTERNS[LSBits][1]

def replaceLSB(frame, payload, LSBits):
    assert isinstance(frame, np.ndarray) 
    assert len(frame)==len(payload)
    ret_data=np.zeros((len(frame), int(8/LSBits)), dtype=np.uint8)
    for i, pixel in enumerate(frame):
        for shift_i, shift in enumerate(range(0, int(8), LSBits)):        
            #pdb.set_trace()
            ret_data[i, shift_i]=(pixel & LSB_PATTERNS[LSBits][0]) | (payload[i]>>shift & LSB_PATTERNS[LSBits][1])
    return ret_data

def extractLSB(frame, LSBits):
    #frame dimensions 0-pixels, 1-shifts
    assert isinstance(frame, np.ndarray)
    #pdb.set_trace()
    assert frame.shape[1]==8/LSBits
    ret_pixels=np.zeros(frame.shape[0], dtype=np.uint8)

    for pix_i in range(frame.shape[0]):
        byte_=0b00000000
        shift=0
        for shift_i in range(frame.shape[1]):
            #print("pix: ", print_byte(pixel))
            v=int(frame[pix_i, shift_i])
            byte_=byte_|((v&LSB_PATTERNS[LSBits][1])<<shift)
            shift+=LSBits
        ret_pixels[pix_i]=byte_
    return ret_pixels

def print_byte(byte):
    return ''.join([str((byte >> i) & 1) for i in range(7, -1, -1)])
def print_arrBytewise(arr):
    for v in arr:
        print(print_byte(v))
        
#decorator for measuring execution time

def timeit(func):
    def wrapper(*args, **kwargs):
        start_tm=time.time()
        res=func(*args, **kwargs)
        print("   it took {:.2f} seconds. ".format(time.time()-start_tm))
        return res
    return wrapper
        


