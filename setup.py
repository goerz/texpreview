#!/usr/bin/env python

from distutils.core import setup

setup(name='texpreview',
      version='0.0.3',
      description='LaTeX Compilation and Preview Utility',
      author='Michael Goerz',
      author_email='goerz@physik.fu-berlin.de',
      url='http://www.physik.fu-berlin.de/~goerz',
      license='GPL',
      packages=['Texpreview'],
      scripts=['texpreview.py']
     )
