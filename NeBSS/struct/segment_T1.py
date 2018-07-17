import nipype.interfaces.io as nio
import nipype.interfaces.fsl as fsl
import nipype.pipeline.engine as pe
import nipype.interfaces.utility as util
from nipype.interfaces.utility import Function
import os
from pit.dti.prob_tracts import tools

from pit.info_util import neo_vol_util
import time


pt_info = neo_vol_util()

data = pt_info['parent_dir']


PCA = pt_info['PCA']
pid = [pt_info['PID']]

configfile = os.path.abspath('./FNIRTconfig.cnf')
T2_Template =os.path.abspath('../res/NeonatalAtlas2/template_T2.nii.gz')

tissuelist = ['brainstem.nii.gz', 'cerebellum.nii.gz',
              'cortex.nii.gz', 'csf.nii.gz', 'dgm.nii.gz',
              'wm.nii.gz', 'brainmask.nii.gz']

TissueList = [os.path.abspath('../res/NeonatalAtlas2/') +
              '/'+ tissue for tissue in tissuelist]


info = dict( T2=[['pid']])

infosource = pe.Node(interface=util.IdentityInterface(fields=['pid']),
                     name="infosource")
infosource.iterables = ('pid', pid)


datasource = pe.Node(interface=nio.DataGrabber(infields=['pid'],
                                               outfields=info.keys()),
                     name = 'datasource')

datasource.inputs.template = "%s"
datasource.inputs.base_directory=data
datasource.inputs.field_template = dict(T2=('%s_T23D.nii.gz'))
datasource.inputs.template_args = info
datasource.inputs.sort_filelist=False

cropT2 = pe.Node(interface=fsl.ExtractROI(), name = 'cropT2')
cropT2.inputs.x_min = pt_info['T2_crop_box'][0]
cropT2.inputs.x_size = pt_info['T2_crop_box'][1] - pt_info['T2_crop_box'][0]
cropT2.inputs.y_min = pt_info['T2_crop_box'][2]
cropT2.inputs.y_size = pt_info['T2_crop_box'][3] - pt_info['T2_crop_box'][2]
cropT2.inputs.z_min = pt_info['T2_crop_box'][4]
cropT2.inputs.z_size = pt_info['T2_crop_box'][5] - pt_info['T2_crop_box'][4]


betT2 = pe.Node(interface=fsl.BET(),name='betT2')
betT2.inputs.frac=0.2
betT2.inputs.robust=True
betT2.inputs.center = pt_info['T2_center']


FastSeg = pe.Node(interface=fsl.FAST(), name = 'FastSeg')
FastSeg.inputs.terminal_output = 'stream'
FastSeg.inputs.output_biascorrected = True
FastSeg.inputs.img_type = 1


get_T2_template = pe.Node(interface=fsl.ExtractROI(), name = 'get_T2_template')
#extract_b0.inputs.t_min = 0
get_T2_template.inputs.t_size = 1
get_T2_template.inputs.in_file = T2_Template


T1linTemplate = pe.Node(interface=fsl.FLIRT(), name='T1linTemplate')
#T1linTemplate.inputs.reference=Template
T1linTemplate.inputs.dof = 12
T1linTemplate.inputs.searchr_x = [-180, 180]
T1linTemplate.inputs.searchr_y = [-180, 180]
T1linTemplate.inputs.searchr_z = [-180, 180]

inverse_T2_matrix = pe.Node(interface=fsl.ConvertXFM(), name='inverse_T2_matrix')
inverse_T2_matrix.inputs.invert_xfm = True

T2warpTemplate=pe.Node(interface=fsl.FNIRT(), name='T2warpTemplate')
T2warpTemplate.inputs.field_file=True
T2warpTemplate.inputs.config_file=configfile

inverse_T2_warp=pe.Node(interface=tools.InvWarp(), name='inverse_T2_warp')


apply_T2_warp=pe.MapNode(interface=fsl.ApplyWarp(), name='apply_T2_warp',
                         iterfield=['in_file'])
apply_T2_warp.inputs.interp='nn'


get_masks = pe.MapNode(interface=fsl.ExtractROI(), name = 'get_masks',
                              iterfield=['in_file'])
get_masks.inputs.t_size = 1
get_masks.inputs.in_file = TissueList


def get_index(PCA):
    if PCA >= 44:
        return 16
    elif PCA <= 28:
        return 0
    else:
        return PCA - 28

get_template_index = pe.Node(name='get_template_index',
                    interface = util.Function(input_names=['PCA'],
                                         output_names=['index'],
                                         function = get_index))
get_template_index.inputs.PCA = PCA

datasink = pe.Node(interface=nio.DataSink(), name='datasink')
datasink.inputs.base_directory = data+'SegT1/Outputs'
datasink.inputs.substitutions = [('_apply_T2_warp', ''),
                                 ('_T23D_roi_brain_restore_warped', '_T2_StdSpace'),
                                 ('_T23D_roi_brain_restore','_T2_Bias_Corrected'),
                                 ('T23D_roi_brain_pve', 'pve'),
                                 ('_roi_warp', ''),
                                 ('_pid_','')]


SegT2 = pe.Workflow(name='SegT2')
SegT2.base_dir = data
SegT2.connect([
                  (infosource, datasource, [('pid', 'pid')]),
                      (datasource, cropT2, [('T2', 'in_file')]),
                           (cropT2, betT2, [('roi_file', 'in_file')]),
                          (betT2, FastSeg, [('out_file', 'in_files')]),
                  (FastSeg, T2linTemplate, [('restored_image', 'in_file')]),
     (get_template_index, get_T2_template, [('index', 't_min')]),
          (get_T2_template, T2linTemplate, [('roi_file', 'reference')]),
                 (FastSeg, T2warpTemplate, [('restored_image', 'in_file')]),
           (T2linTemplate, T2warpTemplate, [('out_matrix_file', 'affine_file')]),
         (get_T1_template, T1warpTemplate, [('roi_file', 'ref_file')]),
         (T2warpTemplate, inverse_T2_warp, [('field_file', 'in_file')]),
                (FastSeg, inverse_T2_warp, [('restored_image', 'ref_file')]),
           (get_template_index, get_masks, [('index', 't_min')]),
                (get_masks, apply_T2_warp, [('roi_file', 'in_file')]),
          (inverse_T2_warp, apply_T2_warp, [('out_file', 'field_file')]),
                  (FastSeg, apply_T2_warp, [('restored_image', 'ref_file')]),
                (T2warpTemplate, datasink, [('warped_file', 'T2_Standard_Space.@T1W')]),
                       (FastSeg, datasink, [('partial_volume_files', 'Fast_PVE.@FPVE')]),
                 (apply_T2_warp, datasink, [('out_file', 'T2_Tissue_Classes.@T2TC')]),
                       (FastSeg, datasink, [('restored_image',
                                                    'T2_Bias_Corrected.@T1B')])
                                ])

from nipype.interfaces.fsl import ImageStats
from pit.vis import colormaps
from pit.vis.map_maker import MapMaker

def get_volume(mask):
    """
    Fslstats -V returns volume [voxels mm3]
    Fslstats -M returns mean value of non-zero voxels
    Multiplying these gives the partial volume estimate
    """
    Volume = ImageStats(in_file = mask, op_string = '-V -M')
    Vout=Volume.run()
    outstat = Vout.outputs.out_stat
    return outstat[1] * outstat[2]

def output_volume(parent_dir, pid, con):
    mskdir = parent_dir+'SegT1/Outputs/'+str(con)+'_Tissue_Classes/'+pid+'/'
    bs_vol = get_volume(mskdir+'0/brainstem.nii.gz')
    cb_vol = get_volume(mskdir+'1/cerebellum.nii.gz')
    ctx_vol = get_volume(mskdir+'2/cortex.nii.gz')
    csf_vol = get_volume(mskdir+'3/csf.nii.gz')
    dgm_vol = get_volume(mskdir+'4/dgm.nii.gz')
    wm_vol = get_volume(mskdir+'5/wm.nii.gz')
    return [con, bs_vol, cb_vol, ctx_vol, csf_vol, dgm_vol, wm_vol]




def create_image(parent_dir, pid, con, center, savefile):
    sourcedir = parent_dir+'SegT2/Outputs/'
    bg = sourcedir+con+'_Bias_Corrected/'+pid+'/'+pid+'_'+con+'_Bias_Corrected.nii.gz'
    mskdir = sourcedir+con+'_Tissue_Classes/'+pid+'/'
    image = MapMaker(bg)
    image.add_overlay(mskdir+'3/csf.nii.gz', 0.05, 1, colormaps.csf(), alpha = 0.7)
    image.add_overlay(mskdir+'2/cortex.nii.gz', 0.05, 1, colormaps.cortex(), alpha = 0.7) 
    image.add_overlay(mskdir+'0/brainstem.nii.gz', 0.05, 1, colormaps.brainstem(), alpha = 0.7)
    image.add_overlay(mskdir+'1/cerebellum.nii.gz', 0.05, 1, colormaps.cerebellum(), alpha = 0.7)
    image.add_overlay(mskdir+'4/dgm.nii.gz', 0.05, 1, colormaps.dgm(), alpha = 0.7) 
    image.add_overlay(mskdir+'5/wm.nii.gz', 0.05, 1, colormaps.wm(), alpha = 0.7) 
    image.save_strip(center[0], center[1], center[2], 20, savefile+'.png')



if __name__ == '__main__':
    start = time.time()
    SegT2.write_graph()
    SegT2.run()
    finish = (time.time() - start) / 60

    print 'Time taken: {0:.7} minutes'.format(finish)

    pid = pid[0]
    print pid
    T2Vols = output_volume(data, pid, 'T2')


    with open(data+'/SegT1/Outputs/Metrics.csv', 'wb') as f:
        f.write('Contrast,Brainstem,Cerebellum, Cortex, CSF, DGM, WM\n')
        f.write('{0},{1:.7},{2:.7},{3:.7},{4:.7},{5:.7},{6:.7}\n'.format(*T1Vols))

    T2Save = pt_info['parent_dir'] + 'SegT2/Outputs/'+pid+'_T2_Segmentation'

    create_image(data, pid, 'T2', pt_info['T2_center'],T2Save)










