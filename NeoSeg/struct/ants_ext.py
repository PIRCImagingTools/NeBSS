"""The ants module provides basic functions for interfacing with ants functions.

   Change directory to provide relative paths for doctests
   >>> import os
   >>> filepath = os.path.dirname( os.path.realpath( __file__ ) )
   >>> datadir = os.path.realpath(os.path.join(filepath, '../../testing/data'))
   >>> os.chdir(datadir)
"""

from nipype.interfaces.base import (TraitedSpec, File, traits,isdefined)
from nipype.interfaces.ants.base import ANTSCommand, ANTSCommandInputSpec
import os
from nipype.interfaces.base import InputMultiPath
from nipype.utils.filemanip import split_filename
import numpy as np


class ANTSInputSpec(ANTSCommandInputSpec):
    dimension = traits.Enum(3, 2, argstr='%d', usedefault=False,
                            position=1, desc='image dimension (2 or 3)')
    fixed_image = InputMultiPath(File(exists=True), mandatory=True,
                                 desc=('image to apply transformation to (generally a coregistered '
                                       'functional)'))
    moving_image = InputMultiPath(File(exists=True), argstr='%s',
                                  mandatory=True,
                                  desc=('image to apply transformation to (generally a coregistered '
                                        'functional)'))

    metric = traits.List(traits.Enum('CC', 'MI', 'SMI', 'PR', 'SSD',
                         'MSQ', 'PSE'), mandatory=True, desc='')

    metric_weight = traits.List(traits.Float(), requires=['metric'], desc='')
    radius = traits.List(traits.Int(), requires=['metric'], desc='')

    output_transform_prefix = traits.Str('out', usedefault=True,
                                         argstr='--output-naming %s',
                                         mandatory=True, desc='')
    transformation_model = traits.Enum('Diff', 'Elast', 'Exp', 'Greedy Exp',
                                       'SyN', argstr='%s', mandatory=True,
                                       desc='')
    gradient_step_length = traits.Float(
        requires=['transformation_model'], desc='')
    number_of_time_steps = traits.Float(
        requires=['gradient_step_length'], desc='')
    delta_time = traits.Float(requires=['number_of_time_steps'], desc='')
    symmetry_type = traits.Float(requires=['delta_time'], desc='')

    use_histogram_matching = traits.Bool(
        argstr='%s', default=True, usedefault=True)
    number_of_iterations = traits.List(
        traits.Int(), argstr='--number-of-iterations %s', sep='x')
    smoothing_sigmas = traits.List(
        traits.Int(), argstr='--gaussian-smoothing-sigmas %s', sep='x')
    subsampling_factors = traits.List(
        traits.Int(), argstr='--subsampling-factors %s', sep='x')
    affine_gradient_descent_option = traits.List(traits.Float(), argstr='%s')

    mi_option = traits.List(traits.Int(), argstr='--MI-option %s', sep='x')
    regularization = traits.Enum('Gauss', 'DMFFD', argstr='%s', desc='')
    regularization_gradient_field_sigma = traits.Float(
        requires=['regularization'], desc='')
    regularization_deformation_field_sigma = traits.Float(
        requires=['regularization'], desc='')
    number_of_affine_iterations = traits.List(
        traits.Int(), argstr='--number-of-affine-iterations %s', sep='x')


class ANTSOutputSpec(TraitedSpec):
    affine_transform = File(exists=True, desc='Affine transform file')
    warp_transform = File(desc='Warping deformation field')
    warp_transform_x = File(exists=True, desc='X Component of warp field')
    warp_transform_y = File(exists=True, desc='Y Component of warp field')
    warp_transform_z = File(exists=True, desc='Z Component of warp field')
    inverse_warp_transform = File(desc='Inverse warping deformation field')
    inverse_warp_transform_x = File(exists=True, desc='X Component of inverse warp field')
    inverse_warp_transform_y = File(exists=True, desc='Y Component of inverse warp field')
    inverse_warp_transform_z = File(exists=True, desc='Z Component of inverse warp field')
    #metaheader = File(exists=True, desc='VTK metaheader .mhd file')
    #metaheader_raw = File(exists=True, desc='VTK metaheader .raw file')


class ANTS(ANTSCommand):

    """


    Examples
    --------

    >>> from nipype.interfaces.ants import ANTS
    >>> ants = ANTS()
    >>> ants.inputs.dimension = 3
    >>> ants.inputs.output_transform_prefix = 'MY'
    >>> ants.inputs.metric = ['CC']
    >>> ants.inputs.fixed_image = ['T1.nii']
    >>> ants.inputs.moving_image = ['resting.nii']
    >>> ants.inputs.metric_weight = [1.0]
    >>> ants.inputs.radius = [5]
    >>> ants.inputs.transformation_model = 'SyN'
    >>> ants.inputs.gradient_step_length = 0.25
    >>> ants.inputs.number_of_iterations = [50, 35, 15]
    >>> ants.inputs.use_histogram_matching = True
    >>> ants.inputs.mi_option = [32, 16000]
    >>> ants.inputs.regularization = 'Gauss'
    >>> ants.inputs.regularization_gradient_field_sigma = 3
    >>> ants.inputs.regularization_deformation_field_sigma = 0
    >>> ants.inputs.number_of_affine_iterations = [10000,10000,10000,10000,10000]
    >>> ants.cmdline
    'ANTS 3 --MI-option 32x16000 --image-metric CC[ T1.nii, resting.nii, 1, 5 ] --number-of-affine-iterations 10000x10000x10000x10000x10000 --number-of-iterations 50x35x15 --output-naming MY --regularization Gauss[3.0,0.0] --transformation-model SyN[0.25] --use-Histogram-Matching 1'
    """
    _cmd = 'ANTS'
    input_spec = ANTSInputSpec
    output_spec = ANTSOutputSpec

    def _image_metric_constructor(self):
        retval = []
        intensityBased = ['CC', 'MI', 'SMI', 'PR', 'SSD', 'MSQ']
        pointSetBased = ['PSE', 'JTB']
        for ii in range(len(self.inputs.moving_image)):
            if self.inputs.metric[ii] in intensityBased:
                retval.append(
                    '--image-metric %s[ %s, %s, %g, %d ]' % (self.inputs.metric[ii],
                                                             self.inputs.fixed_image[
                                                                 ii],
                                                             self.inputs.moving_image[
                                                                 ii],
                                                             self.inputs.metric_weight[
                                                                 ii],
                                                             self.inputs.radius[ii]))
            elif self.inputs.metric[ii] == pointSetBased:
                pass
                # retval.append('--image-metric %s[%s, %s, ...'.format(self.inputs.metric[ii], self.inputs.fixed_image[ii], self.inputs.moving_image[ii], ...))
        return ' '.join(retval)

    def _transformation_constructor(self):
        model = self.inputs.transformation_model
        stepLength = self.inputs.gradient_step_length
        timeStep = self.inputs.number_of_time_steps
        deltaTime = self.inputs.delta_time
        symmetryType = self.inputs.symmetry_type
        retval = ['--transformation-model %s' % model]
        parameters = []
        for elem in (stepLength, timeStep, deltaTime, symmetryType):
            if not elem is traits.Undefined:
                parameters.append('{0}'.format(elem))
        if len(parameters) > 0:
            if len(parameters) > 1:
                parameters = ','.join(parameters)
            else:
                parameters = ''.join(parameters)
            retval.append('[%s]' % parameters)
        return ''.join(retval)

    def _regularization_constructor(self):
        return '--regularization {0}[{1},{2}]'.format(self.inputs.regularization,
                                                      self.inputs.regularization_gradient_field_sigma,
                                                      self.inputs.regularization_deformation_field_sigma)

    def _affine_gradient_descent_option_constructor(self):
        retval = ['--affine-gradient-descent-option']
        values = self.inputs.affine_gradient_descent_option
        defaults = [0.1, 0.5, 1.e-4, 1.e-4]
        for ii in range(len(defaults)):
            try:
                defaults[ii] = values[ii]
            except IndexError:
                break
        stringList = [('%g' % defaults[index]) for index in range(4)]
        parameters = 'x'.join(stringList)
        retval.append(parameters)
        return ' '.join(retval)

    def _format_arg(self, opt, spec, val):
        if opt == 'moving_image':
            return self._image_metric_constructor()
        elif opt == 'transformation_model':
            return self._transformation_constructor()
        elif opt == 'regularization':
            return self._regularization_constructor()
        elif opt == 'affine_gradient_descent_option':
            return self._affine_gradient_descent_option_constructor()
        elif opt == 'use_histogram_matching':
            if self.inputs.use_histogram_matching:
                return '--use-Histogram-Matching 1'
            else:
                return '--use-Histogram-Matching 0'
        return super(ANTS, self)._format_arg(opt, spec, val)

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs['affine_transform'] = os.path.abspath(
            self.inputs.output_transform_prefix + 'Affine.txt')
        outputs['warp_transform'] = os.path.abspath(
            self.inputs.output_transform_prefix + 'Warp.nii.gz')
        outputs['warp_transform_x'] = os.path.abspath(
            self.inputs.output_transform_prefix + 'Warpxvec.nii.gz')
        outputs['warp_transform_y'] = os.path.abspath(
            self.inputs.output_transform_prefix + 'Warpyvec.nii.gz')
        outputs['warp_transform_z'] = os.path.abspath(
            self.inputs.output_transform_prefix + 'Warpzvec.nii.gz')
        outputs['inverse_warp_transform'] = os.path.abspath(
            self.inputs.output_transform_prefix + 'InverseWarp.nii.gz')
        outputs['inverse_warp_transform_x'] = os.path.abspath(
            self.inputs.output_transform_prefix + 'InverseWarpxvec.nii.gz')
        outputs['inverse_warp_transform_y'] = os.path.abspath(
            self.inputs.output_transform_prefix + 'InverseWarpyvec.nii.gz')
        outputs['inverse_warp_transform_z'] = os.path.abspath(
            self.inputs.output_transform_prefix + 'InverseWarpzvec.nii.gz')
        #outputs['metaheader'] = os.path.abspath(self.inputs.output_transform_prefix + 'velocity.mhd')
        #outputs['metaheader_raw'] = os.path.abspath(self.inputs.output_transform_prefix + 'velocity.raw')
        return outputs


class WarpImageMultiTransformInputSpec(ANTSCommandInputSpec):
    dimension = traits.Enum(3, 2, argstr='%d', usedefault=True,
                            desc='image dimension (2 or 3)', position=1)
    input_image = File(argstr='%s', mandatory=True,
                       desc=('image to apply transformation to (generally a '
                              'coregistered functional)'), position=2)
    output_image = File(genfile=True, hash_files=False, argstr='%s',
                        desc=('name of the output warped image'), position = 3, xor=['out_postfix'])
    out_postfix = File("_wimt", usedefault=True, hash_files=False,
                       desc=('Postfix that is prepended to all output '
                             'files (default = _wimt)'), xor=['output_image'])
    reference_image = File(argstr='-R %s', xor=['tightest_box'],
                           desc='reference image space that you wish to warp INTO')
    tightest_box = traits.Bool(argstr='--tightest-bounding-box',
                               desc=('computes tightest bounding box (overrided by '
                                     'reference_image if given)'),
                               xor=['reference_image'])
    reslice_by_header = traits.Bool(argstr='--reslice-by-header',
                                    desc=('Uses orientation matrix and origin encoded in '
                                          'reference image file header. Not typically used '
                                          'with additional transforms'))
    use_nearest = traits.Bool(argstr='--use-NN',
                              desc='Use nearest neighbor interpolation')
    use_bspline = traits.Bool(argstr='--use-BSpline',
                              desc='Use 3rd order B-Spline interpolation')
    transformation_series = InputMultiPath(argstr='%s',
                                           desc='transformation file(s) to be applied',
                                           mandatory=True, position=-1)
    invert_affine = traits.List(traits.Int,
                                desc=('List of Affine transformations to invert.'
                                      'E.g.: [1,4,5] inverts the 1st, 4th, and 5th Affines '
                                      'found in transformation_series. Note that indexing '
                                      'starts with 1 and does not include warp fields. Affine '
                                      'transformations are distinguished '
                                      'from warp fields by the word "affine" included in their filenames.'))


class WarpImageMultiTransformOutputSpec(TraitedSpec):
    output_image = File(exists=True, desc='Warped image')


class WarpImageMultiTransform(ANTSCommand):
    """Warps an image from one space to another

    Examples
    --------

    >>> from nipype.interfaces.ants import WarpImageMultiTransform
    >>> wimt = WarpImageMultiTransform()
    >>> wimt.inputs.input_image = 'structural.nii'
    >>> wimt.inputs.reference_image = 'ants_deformed.nii.gz'
    >>> wimt.inputs.transformation_series = ['ants_Warp.nii.gz','ants_Affine.txt']
    >>> wimt.cmdline
    'WarpImageMultiTransform 3 structural.nii structural_wimt.nii -R ants_deformed.nii.gz ants_Warp.nii.gz ants_Affine.txt'

    >>> wimt = WarpImageMultiTransform()
    >>> wimt.inputs.input_image = 'diffusion_weighted.nii'
    >>> wimt.inputs.reference_image = 'functional.nii'
    >>> wimt.inputs.transformation_series = ['func2anat_coreg_Affine.txt','func2anat_InverseWarp.nii.gz','dwi2anat_Warp.nii.gz','dwi2anat_coreg_Affine.txt']
    >>> wimt.inputs.invert_affine = [1]
    >>> wimt.cmdline
    'WarpImageMultiTransform 3 diffusion_weighted.nii diffusion_weighted_wimt.nii -R functional.nii -i func2anat_coreg_Affine.txt func2anat_InverseWarp.nii.gz dwi2anat_Warp.nii.gz dwi2anat_coreg_Affine.txt'

    """

    _cmd = 'WarpImageMultiTransform'
    input_spec = WarpImageMultiTransformInputSpec
    output_spec = WarpImageMultiTransformOutputSpec

    def _gen_filename(self, name):
        if name == 'output_image':
            _, name, ext = split_filename(
                os.path.abspath(self.inputs.input_image))
            return ''.join((name, self.inputs.out_postfix, ext))
        return None

    def _format_arg(self, opt, spec, val):
        if opt == 'transformation_series':
            series = []
            affine_counter = 0
            for transformation in val:
                if "affine" in transformation.lower() and \
                        isdefined(self.inputs.invert_affine):
                    affine_counter += 1
                    if affine_counter in self.inputs.invert_affine:
                        series += '-i',
                series += [transformation]
            return ' '.join(series)
        return super(WarpImageMultiTransform, self)._format_arg(opt, spec, val)

    def _list_outputs(self):
        outputs = self._outputs().get()
        if isdefined(self.inputs.output_image):
            outputs['output_image'] = os.path.abspath(self.inputs.output_image)
        else:
            outputs['output_image'] = os.path.abspath(
                self._gen_filename('output_image'))
        return outputs

