import csv
from nipype.interfaces.fsl import ImageStats


def get_volume(mask, thresh):
    """
    Fslstats -V returns volume [voxels mm3]
    Fslstats -M returns mean value of non-zero voxels
    Multiplying these gives the partial volume estimate
    """
    Volume = ImageStats(in_file = mask, op_string = '-l {0} -V'.format(thresh))
    Vout=Volume.run()
    outstat = Vout.outputs.out_stat
    return outstat[1]

def output_volume(row,parent_dir):
    """ MAKE SURE STRUCTURES MATCH CSV ORDER """
    ID = row[0]
    mskdir = parent_dir+ID+'/SegT2/Outputs/T2_Tissue_Classes/'
    bs_vol = get_volume(mskdir+'0/brainstem.nii.gz', row[1])
    cb_vol = get_volume(mskdir+'1/cerebellum.nii.gz', row[2])
    ctx_vol = get_volume(mskdir+'2/cortex.nii.gz', row[3])
    dgm_vol = get_volume(mskdir+'4/dgm.nii.gz', row[4])
    wm_vol = get_volume(mskdir+'5/wm.nii.gz', row[5])
    csf_vol = get_volume(mskdir+'3/csf.nii.gz', row[6])
    return [ID,bs_vol, cb_vol, ctx_vol, csf_vol, dgm_vol, wm_vol]

def get_partial(row, parent_dir):
    ID = row[0]
    with open(parent_dir+ID+'/SegT2/Outputs/Metrics.csv') as f:
        reader = csv.reader(f, delimiter=',')
        reader.next()
        return reader.next()

parent_dir = '/home/pirc/Desktop/Alex_Seg_Transfered/'
in_file= parent_dir+'CHD_Thresholds.csv'
out_file = parent_dir+'thresh_vols_new.csv'

thresh = []
with open(in_file, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    headers = reader.next()
    print headers
    for row in reader:
        thresh.append(row)

with open(out_file, 'wb') as f:
    f.write('{0},{1},{2},{3},{4},{5},{6}\n'.format(*headers))
    for row in thresh:
        print 'running subject {0}'.format(row[0])
        f.write('{0},{1:.7},{2:.7},\
                 {3:.7},{4:.7},{5:.7},{6:.7},'.format(
            *output_volume(row, parent_dir)))
        f.write('{0},{1:.7},{2:.7},\
                 {3:.7},{4:.7},{5:.7},{6:.7},\n'.format(
                     *get_partial(row, parent_dir)))

