'''
Created on Mar 19, 2013

@author: rafa
'''


from nipype.interfaces.base import (
    TraitedSpec,
    File,
    traits,
    BaseInterface,
    BaseInterfaceInputSpec
    )
from nipype.interfaces.fsl.base import FSLCommand, FSLCommandInputSpec
import os
from nipype.interfaces.traits_extension import isdefined
from nipype.utils.filemanip import split_filename

class InvWarpInputSpec(FSLCommandInputSpec):

    in_file = File(desc='filename for warp/shiftmap transform',
                  argstr=' -w %s',
                  position=1,
                  mandatory=True,
                  exists=True)


    ref_file = File(desc='filename for new brain-extracted reference image',
                    argstr='-r %s',
                    position=2)

    options = traits.Str(desc='other options',
                    argstr='%s')


    out_file = File(desc='filename for output (inverse warped) image',
                   argstr='-o %s',
                   position=3,
                   genfile=True)

class InvWarpOutputSpec(TraitedSpec):
    out_file = File(desc='Inverse warped image',
                   exists=True)

class InvWarp(FSLCommand):

    _cmd = 'invwarp'

    input_spec = InvWarpInputSpec
    output_spec = InvWarpOutputSpec


    def _gen_filename(self, name):
        """Generate output file name
"""
        if name == 'out_file':
            _, fname, ext = split_filename(self.inputs.in_file)
            return (fname+ '_invw'+ext)


    def _list_outputs(self):
        outputs = self.output_spec().get()

        if not isdefined(self.inputs.out_file):
            outputs['out_file'] = os.path.abspath(self._gen_filename('out_file'))
        else:
            outputs['out_file'] = os.path.abspath(self.inputs.out_file)

        return outputs

class WarpDoneInputSpec(BaseInterfaceInputSpec):
    warped = traits.ListStr(desc='just check for file',mandatory=True, exists=True)

class WarpDoneOutputSpec(TraitedSpec):
    done = traits.Bool(desc='done')

class WarpDone(BaseInterface):
    input_spec = WarpDoneInputSpec
    output_spec = WarpDoneOutputSpec

    def _run_interface(self, runtime):
        self.done = True
        return runtime

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['done'] =self.done
        return outputs






