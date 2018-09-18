from nipype.interfaces.fsl import ImageStats
import nipype.pipeline.engine as pe
import nipype.interfaces.fsl as fsl
import fnmatch
import os


def check_for_fast(seg_dir):
    output_dir = os.path.join(seg_dir, "Outputs/Fast_PVE")
    pve_4 = [n for n in fnmatch.filter(os.listdir(output_dir),
                                       "*pve_3.nii.gz")
             if os.path.isfile(os.path.join(output_dir, n))]
    if pve_4:
        return True
    else:
        return False

# TODO: Run FAST 4 classes


def run_fast(in_file, contrast):
    if contrast == "T2":
        img_type = 2
    elif contrast == "T1":
        img_type = 1
    FastSeg = pe.Node(interface=fsl.FAST(), name='FastSeg')
    FastSeg.inputs.img_type = img_type
    FastSeg.inputs.number_classes = 4
    FastSeg.inputs.in_file = in_file

# TODO: Use FAST to threshold

# TODO: Output volumes


def get_thresh_vol(prob_map, tissue_class):
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

    home_dir = "/home/rafa/Neonates/PT_028/SegT2"

    print(check_for_fast(home_dir))
