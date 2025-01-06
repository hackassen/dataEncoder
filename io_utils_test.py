from io_utils import imset_provider
"""

"""

p=imset_provider("/home/hackassen/works/dataEncoder/x-ray_dataset/")
for i, (imid, im) in enumerate(p.iter()):
    print(imid, im.shape)
    if i==3: break