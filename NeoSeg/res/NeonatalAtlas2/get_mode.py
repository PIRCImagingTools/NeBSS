
import numpy as np
from nipy import load_image, save_image
from nipy.core.api import Image

import time, os

IMG = load_image(os.path.abspath('./brainstem.nii.gz'))
new_coord = IMG[:,:,:,0].coordmap
data = IMG.get_data()

def get_mode(array):
    MODE =np.zeros(array.shape[:3])
    for i in xrange(array.shape[0]):
        for j in xrange(array.shape[1]):
            for k in xrange(array.shape[2]):
                u, indices = np.unique(array[i,j,k,:], return_inverse=True)
                mode = u[np.argmax(np.bincount(indices))] 
                print "mode at {0},{1},{2} = {3}".format(i,j,k,mode)
                MODE[i,j,k] = mode

    return MODE

start = time.time() 
mode = get_mode(data) 
print "Finished at {0} seconds".format(time.time()-start)
mode_image = Image(MODE, new_coord)
outfile = 'BS_MODE.nii'
save_image(mode_image, outfile)
