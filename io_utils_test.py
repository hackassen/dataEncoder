from io_utils import imset_provider, video_provider
"""

"""

#p=imset_provider("/home/hackassen/works/dataEncoder/x-ray_dataset/")
#for i, (imid, im) in enumerate(p.iter()):
#    print(imid, im.shape)
#    if i==3: break

import matplotlib.pyplot as plt
import cv2

p=video_provider("/home/hackassen/Downloads/movies/[Udemy] Python Programming Machine Learning, Deep Learning (05.2021)/7. Artificial Neural Network/")
for i, (imid, im) in enumerate(p.iter()):
    #print(imid, im.shape)
    if i%5 ==0:
        cv2.imshow('Frame', im)
    
    
    if cv2.waitKey(25)&0xFF==ord('q'): break
    
    #plt.imshow(im)
    #plt.waitforbuttonpress()
    if i==3000: break
