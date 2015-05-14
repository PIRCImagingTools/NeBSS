import nipype.interfaces.io as nio
import nipype.interfaces.fsl as fsl
import  ants_ext as ants
import nipype.pipeline.engine as pe
import nipype.interfaces.utility as util
import os,json, sys
import tools
import time
from nipype import config

def determine_path():
    """
    determines the local path of the module on the OS
    """
    try:
        root = __file__
        if os.path.islink(root):
            root = os.path.realpath(root)
        return os.path.dirname(os.path.abspath(root))
    except:
        print "No __file__ variable"
        print "Problem with installation?"
        sys.exit()

local_path = determine_path()
print "local path: "+local_path
fnirt_config = os.path.abspath(local_path+'/../res/fdm_FNIRT.cnf')

config_file = os.environ['fdm_config']
with open(config_file, 'r') as f:
    cfg = json.load(f)

parent_dir = cfg['parent_dir']
pca = int(cfg['pca'])
pid = cfg['pid']

configfile = os.path.abspath(local_path+'/../res/FNIRTconfig.cnf')
albert_config = os.path.abspath(local_path+'/../res/ALBERT.cnf')
T2_Template =os.path.abspath(local_path+'/../res/NeonatalAtlas2/template_T2.nii.gz')

tissuelist = ['brainstem.nii.gz', 'cerebellum.nii.gz',
              'cortex.nii.gz', 'csf.nii.gz', 'dgm.nii.gz',
              'wm.nii.gz', 'brainmask.nii.gz',
              'ivcsf.nii.gz','stcsf.nii.gz', 'itcsf.nii.gz']

TissueList = [os.path.abspath(local_path+'/../res/NeonatalAtlas2/') +'/'+
               tissue for tissue in tissuelist]

config.set('execution','crashdump_dir',parent_dir)


cropT2 = pe.Node(interface=fsl.ExtractROI(), name = 'cropT2')
cropT2.inputs.x_min =  cfg['T2_crop_box'][0]
cropT2.inputs.x_size = cfg['T2_crop_box'][1] - cfg['T2_crop_box'][0]
cropT2.inputs.y_min =  cfg['T2_crop_box'][2]
cropT2.inputs.y_size = cfg['T2_crop_box'][3] - cfg['T2_crop_box'][2]
cropT2.inputs.z_min =  cfg['T2_crop_box'][4]
cropT2.inputs.z_size = cfg['T2_crop_box'][5] - cfg['T2_crop_box'][4]
cropT2.inputs.in_file = cfg['T2_struct']

reorientT2 = pe.Node(interface=fsl.Reorient2Std(), name = 'reorientT2')

betT2 = pe.Node(interface=fsl.BET(),name='betT2')
betT2.inputs.frac=0.2
betT2.inputs.robust=True
betT2.inputs.center = cfg['T2_center']


FastSeg = pe.Node(interface=fsl.FAST(), name = 'FastSeg')
FastSeg.inputs.terminal_output = 'stream'
FastSeg.inputs.output_biascorrected = True
FastSeg.inputs.img_type = 2


get_T2_template= pe.Node(interface=fsl.ExtractROI(),
                         name = 'get_T2_template')
#extract_b0.inputs.t_min = 0
get_T2_template.inputs.t_size = 1
get_T2_template.inputs.in_file = T2_Template


T2linTemplate = pe.Node(interface=fsl.FLIRT(), name='T2linTemplate')
T2linTemplate.inputs.dof = 12
T2linTemplate.inputs.searchr_x = [-180, 180]
T2linTemplate.inputs.searchr_y = [-180, 180]
T2linTemplate.inputs.searchr_z = [-180, 180]

#T2warpTemplate=pe.Node(interface=fsl.FNIRT(), name='T2warpTemplate')
#T2warpTemplate.inputs.field_file=True
#T2warpTemplate.inputs.config_file=configfile

#### REAL PARAMETERS
#T2warpTemplate=pe.Node(interface=ants.ANTS(), name='T2warpTemplate')
#T2warpTemplate.inputs.dimension=3
#T2warpTemplate.inputs.metric=['CC',]
#T2warpTemplate.inputs.metric_weight=[1.0,]
#T2warpTemplate.inputs.radius=[10,]
#T2warpTemplate.inputs.output_transform_prefix='ANTS_OUT'
#T2warpTemplate.inputs.transformation_model='SyN'
#T2warpTemplate.inputs.gradient_step_length=0.25
#T2warpTemplate.inputs.number_of_time_steps=2
#T2warpTemplate.inputs.delta_time=0.01
#T2warpTemplate.inputs.number_of_iterations=[100,100,100,50]
#T2warpTemplate.inputs.regularization='Gauss'
#T2warpTemplate.inputs.regularization_gradient_field_sigma=3
#T2warpTemplate.inputs.regularization_deformation_field_sigma=0

### TEST PARAMETERS
T2warpTemplate=pe.Node(interface=ants.ANTS(), name='T2warpTemplate')
T2warpTemplate.inputs.dimension=3
T2warpTemplate.inputs.metric=['CC',]
T2warpTemplate.inputs.metric_weight=[1.0,]
T2warpTemplate.inputs.radius=[2,]
T2warpTemplate.inputs.output_transform_prefix='ANTS_OUT'
T2warpTemplate.inputs.transformation_model='SyN'
T2warpTemplate.inputs.gradient_step_length=0.8
T2warpTemplate.inputs.number_of_time_steps=2
T2warpTemplate.inputs.delta_time=0.02
T2warpTemplate.inputs.number_of_iterations=[2,2,2,1]
T2warpTemplate.inputs.regularization='Gauss'
T2warpTemplate.inputs.regularization_gradient_field_sigma=3
T2warpTemplate.inputs.regularization_deformation_field_sigma=0

T2warpTemplate.config = {'execution':
                         {'remove_unnuecessary_outputs' : False}
                         }

T2_warp_to_standard=pe.Node(interface=ants.WarpImageMultiTransform(),
                               name='T2_warp_to_standard')


apply_T2_warp=pe.MapNode(interface=ants.WarpImageMultiTransform(),
                         name='apply_T2_warp',
                         iterfield=['input_image'])


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
get_template_index.inputs.PCA = pca


albert_group = cfg['albert_group']
def get_albert_group(group,local_path):
    import os
    groups = {
        '<27':['06','09','15','17','18'],
        '27-30':['08','10','11','12','14','20'],
        '30-36':['07','13','16','19'],
        'Term':['01','02','03','04','05']
    }
    return [os.path.abspath(local_path+'/../res/Albert/volumes/{0}_T2_brain.nii.gz'.format(x))
                              for x in groups[group]]



get_albert_list= pe.Node(name='get_albert_list',
                    interface = util.Function(input_names=['group','local_path'],
                                         output_names=['albert_list'],
                                         function = get_albert_group))
get_albert_list.inputs.group = albert_group
get_albert_list.inputs.local_path = local_path


def get_seg_list(group,local_path):
    import os
    groups = {
        '<27':['06','09','15','17','18'],
        '27-30':['08','10','11','12','14','20'],
        '30-36':['07','13','16','19'],
        'Term':['01','02','03','04','05']
    }
    return [os.path.abspath(local_path+'/../res/Albert/segmentations/ALBERT_{0}_ISG_seg50.nii'.format(x))
                              for x in groups[group]]



get_albert_seg= pe.Node(name='get_albert_seg',
                    interface = util.Function(input_names=['group','local_path'],
                                         output_names=['seg_list'],
                                         function = get_seg_list))
get_albert_seg.inputs.group = albert_group
get_albert_seg.inputs.local_path = local_path

albert_lin = pe.MapNode(interface=fsl.FLIRT(), name='albert_lin', iterfield='in_file')
#T2linTemplate.inputs.reference=Template
albert_lin.inputs.dof = 12
albert_lin.inputs.searchr_x = [-180, 180]
albert_lin.inputs.searchr_y = [-180, 180]
albert_lin.inputs.searchr_z = [-180, 180]


#albert_warp=pe.MapNode(interface=fsl.FNIRT(), name='albert_warp', iterfield=['in_file','affine_file'])
#albert_warp.inputs.field_file=True
#albert_warp.inputs.config_file=albert_config

#### REAL PARAMETERS
#albert_warp=pe.MapNode(interface=ants.ANTS(),
#                       name='albert_warp',
#                       iterfield=['moving_image'])
#albert_warp.inputs.dimension=3
#albert_warp.inputs.metric=['CC',]
#albert_warp.inputs.metric_weight=[1.0,]
#albert_warp.inputs.radius=[10,]
#albert_warp.inputs.output_transform_prefix='ANTS_OUT'
#albert_warp.inputs.transformation_model='SyN'
#albert_warp.inputs.gradient_step_length=0.5
#albert_warp.inputs.number_of_time_steps=5
#albert_warp.inputs.delta_time=0.01
#albert_warp.inputs.number_of_iterations=[100,100,100,50]
#albert_warp.inputs.regularization='Gauss'
#albert_warp.inputs.regularization_gradient_field_sigma=3
#albert_warp.inputs.regularization_deformation_field_sigma=0

#### TEST PARAMETERS
albert_warp=pe.MapNode(interface=ants.ANTS(),
                       name='albert_warp',
                       iterfield=['moving_image'])
albert_warp.inputs.dimension=3
albert_warp.inputs.metric=['CC',]
albert_warp.inputs.metric_weight=[1.0,]
albert_warp.inputs.radius=[2,]
albert_warp.inputs.output_transform_prefix='ANTS_OUT'
albert_warp.inputs.transformation_model='SyN'
albert_warp.inputs.gradient_step_length=0.8
albert_warp.inputs.number_of_time_steps=2
albert_warp.inputs.delta_time=0.01
albert_warp.inputs.number_of_iterations=[2,2,2,2]
albert_warp.inputs.regularization='Gauss'
albert_warp.inputs.regularization_gradient_field_sigma=3
albert_warp.inputs.regularization_deformation_field_sigma=0

albert_warp.config = {'execution':
                         {'remove_unnuecessary_outputs' : False}
                         }

apply_albert_warp=pe.MapNode(interface=ants.WarpImageMultiTransform(),
                             name='apply_albert_warp',
                             iterfield=['input_image','transformation_series'])


AlbertSeg = pe.Workflow(name='AlbertSeg')
AlbertSeg.base_dir = parent_dir+'/SegT2'
AlbertSeg.connect([
                (get_albert_list, albert_lin, [('albert_list','in_file')]),
                    (albert_lin, albert_warp, [('out_file','moving_image')]),
             (albert_warp, apply_albert_warp, [('warp_transform','transformation_series')]),
          (get_albert_seg, apply_albert_warp, [('seg_list', 'input_image')])
])



datasink = pe.Node(interface=nio.DataSink(), name='datasink')
datasink.inputs.base_directory = parent_dir+'/SegT2/Outputs'
datasink.inputs.substitutions = [('_apply_T2_warp', ''),
                                 ('_roi_reoriented_brain_restore_warped', '_T2_StdSpace'),
                                 ('_roi_reoriented_brain_restore','_T2_Bias_Corrected'),
                                 ('_roi_reoriented_brain_pve', 'pve'),
                                 ('_roi_warp', ''),
                                 ('_apply_albert_warp','')]



SegT2 = pe.Workflow(name='SegT2')
SegT2.base_dir = parent_dir
SegT2.connect([
                      (cropT2, reorientT2, [('roi_file', 'in_file')]),
                       (reorientT2, betT2, [('out_file', 'in_file')]),
                          (betT2, FastSeg, [('out_file', 'in_files')]),
                  (FastSeg, T2linTemplate, [('restored_image', 'in_file')]),
     (get_template_index, get_T2_template, [('index', 't_min')]),
          (get_T2_template, T2linTemplate, [('roi_file', 'reference')]),
           (T2linTemplate, T2warpTemplate, [('out_file', 'moving_image')]),
         (get_T2_template, T2warpTemplate, [('roi_file', 'fixed_image')]),
           (get_template_index, get_masks, [('index', 't_min')]),
                (get_masks, apply_T2_warp, [('roi_file', 'input_image')]),
           (T2warpTemplate, apply_T2_warp, [('inverse_warp_transform',
                                                    'transformation_series')]),
                  (FastSeg, apply_T2_warp, [('restored_image', 'reference_image')]),
                      (FastSeg, AlbertSeg, [('restored_image','albert_lin.reference')]),
                      (FastSeg, AlbertSeg, [('restored_image','albert_warp.fixed_image')]),
                      (FastSeg, AlbertSeg, [('restored_image',
                                                     'apply_albert_warp.reference_image')]),
            (FastSeg, T2_warp_to_standard, [('restored_image', 'input_image')]),
     (T2warpTemplate, T2_warp_to_standard, [('warp_transform',
                                                          'transformation_series')]),
           (T2_warp_to_standard, datasink, [('output_image', 'T2_Standard_Space.@T2W')]),
                       (FastSeg, datasink, [('partial_volume_files', 'Fast_PVE.@FPVE')]),
                 (apply_T2_warp, datasink, [('output_image', 'T2_Tissue_Classes.@T2TC')]),
                       (FastSeg, datasink, [('restored_image',
                                                    'T2_Bias_Corrected.@T2B')]),
                     (AlbertSeg, datasink, [('apply_albert_warp.output_image',
                                                                'Reg_Alberts.@MA')])
                                ])

from nipype.interfaces.fsl import ImageStats,Merge
import colormaps
from map_maker import MapMaker
from nipy import load_image, save_image
from nipy.core.api import Image
import numpy as np

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
    mskdir = parent_dir+'/SegT2/Outputs/'+str(con)+'_Tissue_Classes/'
    bs_vol = get_volume(mskdir+'0/brainstem.nii.gz')
    cb_vol = get_volume(mskdir+'1/cerebellum.nii.gz')
    ctx_vol = get_volume(mskdir+'2/cortex.nii.gz')
    csf_vol = get_volume(mskdir+'3/csf.nii.gz')
    dgm_vol = get_volume(mskdir+'4/dgm.nii.gz')
    wm_vol = get_volume(mskdir+'5/wm.nii.gz')
    x_itcsf = get_volume(mskdir+'6/x_itcsf.nii.gz')
    x_ivcsf = get_volume(mskdir+'7/x_ivcsf.nii.gz')
    x_stcsf = get_volume(mskdir+'8/x_stcsf.nii.gz')

    return [con, bs_vol, cb_vol, ctx_vol,
            csf_vol, dgm_vol, wm_vol,
            x_itcsf, x_ivcsf, x_stcsf]



def merge_regs(out_dir, out_file):
    import subprocess, shlex
    folder_list = [out_dir+folder for folder in os.listdir(out_dir)]
    print folder_list
    file_list = [folder+'/'+(os.listdir(folder)[0])
                 for folder in folder_list]
    merger = Merge()
    merger.inputs.in_files = file_list
    merger.inputs.dimension = 't'
    merger.inputs.merged_file = out_file
    print merger.cmdline
    command = shlex.split(merger.cmdline)
    subprocess.call(command)



def get_mode(seg_stack, out_file):
    img = load_image(seg_stack)
    new_coord = img[:,:,:,0].coordmap
    data = img.get_data()
    mode = np.zeros(data.shape[:3])
    for i in xrange(data.shape[0]):
        for j in xrange(data.shape[1]):
            for k in xrange(data.shape[2]):
                u, indices = np.unique(data[i,j,k,:],
                                       return_inverse=True)
                voxel_mode = u[np.argmax(np.bincount(indices))]
                print "mode at {0},{1},{2} = {3}".format(i,j,k,voxel_mode)
                mode[i,j,k] = voxel_mode
    mode_image = Image(mode, new_coord)
    save_image(mode_image, out_file)
    return mode


def create_image(parent_dir, pid, savefile):
    sourcedir = parent_dir+'/SegT2/Outputs/'
    bg = sourcedir+'T2_Bias_Corrected/'+(os.listdir(sourcedir+'T2_Bias_Corrected/')[0])
    mskdir = sourcedir+'T2_Tissue_Classes/'
    image = MapMaker(bg)
    image.add_overlay(mskdir+'3/csf.nii.gz', 0.05, 1, colormaps.csf(), alpha = 0.7)
    image.add_overlay(mskdir+'2/cortex.nii.gz', 0.05, 1, colormaps.cortex(), alpha = 0.7)
    image.add_overlay(mskdir+'0/brainstem.nii.gz', 0.05, 1, colormaps.brainstem(), alpha = 0.7)
    image.add_overlay(mskdir+'1/cerebellum.nii.gz', 0.05, 1, colormaps.cerebellum(), alpha = 0.7)
    image.add_overlay(mskdir+'4/dgm.nii.gz', 0.05, 1, colormaps.dgm(), alpha = 0.7)
    image.add_overlay(mskdir+'5/wm.nii.gz', 0.05, 1, colormaps.wm(), alpha = 0.7)
    image.save_strip_center(savefile+'.png', 20)




start = time.time()
SegT2.write_graph()
SegT2.run()
finish = (time.time() - start) / 60

print 'Time taken: {0:.7} minutes'.format(finish)

pid = pid
print pid
T2Vols = output_volume(parent_dir, pid, 'T2')


with open(parent_dir+'/SegT2/Outputs/Metrics.csv', 'wb') as f:
    f.write('Contrast,Brainstem,Cerebellum, Cortex, CSF, DGM, WM, ITCSF, IVCSF, STCSF\n')
    f.write('{0},{1:.7},{2:.7},{3:.7},{4:.7},{5:.7},{6:.7},{7:.7},{8:.7},{9:.7}\n'.format(*T2Vols))

T2Save = cfg['parent_dir'] + '/SegT2/Outputs/'+pid+'_T2_Segmentation'
AlbertSave = cfg['parent_dir'] + '/SegT2/Outputs/'+pid+'_Albert_WTA'
AlbertFile = cfg['parent_dir'] + '/SegT2/Outputs/'+pid+'_Albert_Stack.nii.gz'
AlbertOutDir = cfg['parent_dir']+'/SegT2/Outputs/Reg_Alberts/'
print AlbertOutDir

merge_regs(AlbertOutDir, AlbertFile)
get_mode(AlbertFile, AlbertSave)
create_image(parent_dir, pid,T2Save)










