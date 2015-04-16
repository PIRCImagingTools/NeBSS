#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='NeoSeg',
      version='0.1',
      description='Neonatal segmentation',
      long_description=open('README').read(),
      author='Rafael Ceschin',
      author_email='rcc10@pitt.edu',
      url='http://github.com/PIRCImagingTools/NeoSeg/',
      packages=find_packages(),
      package_data = {'NeoSeg':['ui/*','res/*']},
      scripts=['neoseg_gui'],
      install_requires=['networkx','nibabel >=1.0',
                        'nipy','nipype >=0.8',
                        'numpy >=1.3','scipy >=0.7',
                        'matplotlib','pillow','ipython'],
      license='BSD'
     )

