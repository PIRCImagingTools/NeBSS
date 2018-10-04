from nipype.interfaces.fsl import ImageStats
import nipype.interfaces.fsl as fsl
import fnmatch
import shutil
import os
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from res.misc import get_albert_labels


def check_for_fast(fast_dir):
    pve_4 = [n for n in fnmatch.filter(os.listdir(fast_dir),
                                       "*pve_3.nii.gz")
             if os.path.isfile(os.path.join(fast_dir, n))]
    if pve_4:
        return True
    else:
        return False


def get_file_name(seg_dir, pattern):
    bias_corrected = [n for n in fnmatch.filter(os.listdir(seg_dir),
                                                pattern)
                      if os.path.isfile(os.path.join(seg_dir, n))]
    return bias_corrected[0]


def run_fast(outputs_dir, in_file, contrast):
    """
    Deletes old Fast outputs and re-runs Fast in the
    old directory.
    Running with 4 classes
    Generally, for a neonatal T2:
        class 0 : CSF/hyperintense WM
        class 1 : WM
        class 2 : GM
        class 3 : Extra-axial CSF/Noise
    """
    fast_dir = os.path.join(outputs_dir, "Fast_PVE")
    [os.remove(os.path.join(fast_dir, n)) for n in os.listdir(fast_dir)]
    shutil.copy2(os.path.join(outputs_dir, "T2_Bias_Corrected", in_file),
                 fast_dir)
    cp_file = os.path.join(fast_dir, in_file)
    if contrast == "T2":
        img_type = 2
    elif contrast == "T1":
        img_type = 1
    os.chdir(fast_dir)
    FastSeg = fsl.FAST()
    FastSeg.inputs.img_type = img_type
    FastSeg.inputs.number_classes = 4
    FastSeg.inputs.output_biascorrected = False
    FastSeg.inputs.in_files = cp_file
    FastSeg.run()


def binarize_mask(mask_in, mask_out):
    pass


def thresh_albert_gm(outputs_dir):
    in_file = os.path.join(outputs_dir,
                           get_file_name(outputs_dir, "*Albert_WTA*"))
    mask_file = os.path.join(outputs_dir, "Fast_PVE", get_file_name(
        os.path.join(outputs_dir, "Fast_PVE"), "*pve_2*"))
    maths = fsl.MultiImageMaths()
    maths.inputs.in_file = in_file
    maths.inputs.op_string = "-mas %s "
    maths.inputs.operand_files = [mask_file]
    maths.inputs.out_file = os.path.join(outputs_dir, "Albert_GM.nii.gz")
    maths.cmdline
    maths.run()


def get_thresh_vol(prob_map):
    """
    Fslstats -V returns volume [voxels mm3]
    Fslstats -M returns mean value of non-zero voxels
    Multiplying these gives the partial volume estimate
    """

    Volume = ImageStats(in_file=prob_map,
                        op_string='-V -M')
    Vout = Volume.run()
    outstat = Vout.outputs.out_stat
    return outstat[1] * outstat[2]


if __name__ == "__main__":

    outputs_dir = os.path.abspath(sys.argv[1])
    fast_dir = os.path.join(outputs_dir, "Fast_PVE")
    tissue_class_dir = os.path.join(outputs_dir, "T2_Tissue_Classes")
    struct_t2 = get_file_name(os.path.join(outputs_dir, "T2_Bias_Corrected"),
                              "*_Bias_Corrected*")

    print(get_albert_labels())

    if check_for_fast(fast_dir):
        print("Checked")
#        thresh_albert_gm(outputs_dir)
#        get_thresh_vol(fast_dir, tissue_class_dir)
    else:
        print("Running FSL Fast on file {0}".format(struct_t2))
        run_fast(outputs_dir, struct_t2, "T2")
        thresh_albert_gm(outputs_dir)
#       get_thresh_vol(fast_dir, tissue_class_dir)
