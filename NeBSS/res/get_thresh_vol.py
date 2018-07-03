import csv
from nipype.interfaces.fsl import ImageStats
from nipype.interfaces.fsl.maths import MathsCommand


def get_volume(mask, thresh, out_file):
    Mask = MathsCommand(in_file = mask,
                        args = "-thr {0} -bin".format(thresh),
                        out_file=out_file)
    Mout = Mask.run()
    Volume = ImageStats(in_file = mask, op_string = '-l {0} -V'.format(thresh))
    Vout=Volume.run()
    outstat = Vout.outputs.out_stat
    return outstat[1]

def output_volume(row,parent_dir):
    """ MAKE SURE STRUCTURES MATCH CSV ORDER """
    ID = row[0]
    mskdir = parent_dir+ID+'/SegT2/Outputs/T2_Tissue_Classes/'
    bs_vol = get_volume(mskdir+'0/brainstem.nii.gz',
                        row[1],
                        mskdir+'0/brainstem_thr.nii.gz')
    cb_vol = get_volume(mskdir+'1/cerebellum.nii.gz', row[2],
                        mskdir+'1/cerebellum_thr.nii.gz')
    ctx_vol = get_volume(mskdir+'2/cortex.nii.gz', row[3],
                         mskdir+'2/cortex_thr.nii.gz')
    dgm_vol = get_volume(mskdir+'4/dgm.nii.gz', row[4],
                         mskdir+'4/dgm_thr.nii.gz')
    wm_vol = get_volume(mskdir+'5/wm.nii.gz', row[5],
                        mskdir+'5/wm_thr.nii.gz')
    csf_vol = get_volume(mskdir+'3/csf.nii.gz', row[6],
                         mskdir+'3/csf_thr.nii.gz')
    itcsf_vol = get_volume(mskdir+'7/itcsf.nii.gz', row[7],
                           mskdir+'7/itcsf_thr.nii.gz')
    ivcsf_vol = get_volume(mskdir+'8/ivcsf.nii.gz', row[8],
                           mskdir+'8/ivcsf_thr.nii.gz')
    stcsf_vol = get_volume(mskdir+'9/stcsf.nii.gz', row[9],
                           mskdir+'9/stcsf_thr.nii.gz')
    return [ID, bs_vol, cb_vol, ctx_vol,
            csf_vol, dgm_vol, wm_vol,
            itcsf_vol, ivcsf_vol, stcsf_vol]

def get_partial(row, parent_dir):
    ID = row[0]
    with open(parent_dir+ID+'/SegT2/Outputs/Metrics.csv') as f:
        reader = csv.reader(f, delimiter=',')
        reader.next()
        return reader.next()

parent_dir = '/home/rafa/Neonates/'
in_file= parent_dir+'thresh.csv'
out_file = parent_dir+'thresh_vols_new.csv'

thresh = []
with open(in_file, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    headers = reader.next()
    print headers
    for row in reader:
        thresh.append(row)

with open(out_file, 'wb') as f:
    f.write('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n'.format(*headers))
    for row in thresh:
        print 'running subject {0}'.format(row[0])
        f.write('{0},{1:.7},{2:.7},\
                 {3:.7},{4:.7},{5:.7},{6:.7},\
                 {7:.7},{8:.7},{9:.7},'.format(
            *output_volume(row, parent_dir)))
        f.write('{0},{1:.7},{2:.7},\
                 {3:.7},{4:.7},{5:.7},{6:.7},\
                 {7:.7},{8:.7},{9:.7},{10:.7}\n'.format(
                     *get_partial(row, parent_dir)))

