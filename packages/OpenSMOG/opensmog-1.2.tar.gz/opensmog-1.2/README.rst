========
OpenSMOG
========

|Citing OpenSMOG|
|PyPI|
|conda-forge|
|ReadTheDocs|
|SMOG server|
|Update|
|GitHub-Stars|

.. |Citing OpenSMOG| image:: https://img.shields.io/badge/cite-OpenSMOG-informational
   :target: https://opensmog.readthedocs.io/en/latest/Reference/citing.html
.. |PyPI| image:: https://img.shields.io/pypi/v/OpenSMOG.svg
   :target: https://pypi.org/project/OpenSMOG/
.. |conda-forge| image:: https://img.shields.io/conda/vn/conda-forge/OpenSMOG.svg
   :target: https://anaconda.org/conda-forge/OpenSMOG
.. |ReadTheDocs| image:: https://readthedocs.org/projects/opensmog/badge/?version=latest
   :target: https://opensmog.readthedocs.io/en/latest/
.. |SMOG server| image:: https://img.shields.io/badge/SMOG-Server-informational
   :target: https://smog-server.org/
.. |Update| image:: https://anaconda.org/conda-forge/opensmog/badges/latest_release_date.svg
   :target: https://anaconda.org/conda-forge/opensmog
.. |GitHub-Stars| image:: https://img.shields.io/github/stars/junioreif/OpenSMOG.svg?style=social
   :target: https://github.com/junioreif/OpenSMOG


`Documentation <https://opensmog.readthedocs.io/>`__
| `Install <https://opensmog.readthedocs.io/en/latest/GettingStarted/install.html>`__
| `Tutorials <https://opensmog.readthedocs.io/en/latest/Tutorials/SBM_CA.html>`__

Overview
========

OpenSMOG is a Python library for performing molecular dynamics simulations using Structure-Based Models. OpenSMOG uses the  `OpenMM <http://openmm.org/>`_. Python API, which supports a wide variety of potential energy functions, including those that are commonly employed in C-alpha and all-atom models.
While it is possible to use this library in a standalone fashion, it is expected that users will generate input files using the SMOG2 software (version 2.4, or later, with the flag :code:`-OpenSMOG`). Details on how to generate OpenSMOG-compatible force fields files can be found in the `SMOG2 User Manual <https://smog-server.org/smog2/>`__.


Citation
========

When using **OpenSMOG** and **SMOG2**, please `use the following references
<https://opensmog.readthedocs.io/en/latest/Reference/citing.html>`__.



Installation
============

The **OpenSMOG** library can be installed via `conda <https://conda.io/projects/conda/>`_ or `pip <https://pypi.org/>`_, or compiled from `source (GitHub) <https://github.com/junioreif/OpenSMOG>`_.

Install via conda
-----------------

The code below will install **OpenSMOG** from `conda-forge <https://anaconda.org/conda-forge/OpenSMOG>`_.

.. code-block:: bash

    conda install -c conda-forge OpenSMOG

Install via pip
-----------------

The code below will install **OpenSMOG** from `PyPI <https://pypi.org/project/OpenSMOG/>`_.

.. code-block:: bash

    pip install OpenSMOG

OpenMM
--------------

The **OpenSMOG** library uses `OpenMM <http://openmm.org/>`_ API to run the molecular dynamics simulations. While the above methods should automatically install OpenMM, you can find additional installation options on the OpenMM page..
    
The following libraries are **required** for installing **OpenSMOG**:

    - `Python <https://www.python.org/>`__ (>=3.6)
    - `NumPy <https://www.numpy.org/>`__ (>=1.14)
    - `lxml <https://lxml.de/>`__ (>=4.6.2)

Installing/Configuring SMOG2
============================

The inputs required for **OpenSMOG** simulations can be generated using `SMOG 2 <https://smog-server.org/smog2>`_ (version 2.4 and later). For a description of the various ways in which you may access SMOG 2 (e.g. Docker/Singularity container, conda, etc), see the README file in the `SMOG 2 GitHub repo <https://github.com/smog-server/SMOG2/>`__. 

Resources
=========

- `Reference Documentation <https://opensmog.readthedocs.io/>`__: Examples, tutorials, and class details.
- `Installing OpenSMOG <https://opensmog.readthedocs.io/en/latest/GettingStarted/install.html#installing-opensmog>`__: Instructions for installing **OpenSMOG**.
- `Installing SMOG2 <https://opensmog.readthedocs.io/en/latest/GettingStarted/install.html#installing-smog2>`__: Instructions for installing **SMOG2**.
- `Issue tracker <https://github.com/smog-server/OpenSMOG/issues>`__: Report issues/bugs or request features.
