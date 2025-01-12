.. Project_Name documentation master file, created by
   sphinx-quickstart on Tue Feb  9 10:52:45 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Carbide Detection documentation!
===========================================

Carbide Detection (carde) is a Python package for the detection of carbides in scanning electron micrographs. 
It is based on the `SimpleITK <https://simpleitk.readthedocs.io/en/master/>`_ library.

Note
----

The code makes a few assumptions regarding the image file names:

1. The image file name ends with an underscore and a number (with leading zeros) before the extension. For example: "WD6mm_05.tif"
2. Matching images are numbered consecutively with the odd number coming first. For example: "WD6mm_05.tif" and "WD6mm_06.tif" or "WD6mm_01.tif" and "WD6mm_02.tif".
   
This means that you should always start with an odd number (e.g. 01) and then image alternately with the SE and InLens detectors.
   
This also means that "WD6mm_02.tif" and "WD6mm_03.tif" will not be considered matching images (because the odd number is larger than the even number).

Installation
============
To install the package, you can use the following command (preferably in a virtual environment):

.. code-block:: bash

   python3 -m pip install carde

Usage
=====

please refer to the following notebooks for examples on how to use the package:

.. toctree::
   :maxdepth: 1
   :caption: Notebooks:

   notebooks/process_image_folder.ipynb

   notebooks/classic_ml_segmentation.ipynb

Documentation
=============

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   source/modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
