.. LUMEX documentation master file, created by
   sphinx-quickstart on Fri Oct 25 15:05:09 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

LUMEX documentation
===================

**Lumerical to Meep Exchange (LUMEX)** is an open-source source-to-source compiler designed to translate `Ansys Lumerical <https://www.ansys.com/products/optics/fdtd>`_ `.lsf` scripts into `Meep <https://meep.readthedocs.io/en/master/>`_-compatible Python code.  


.. toctree::
   :maxdepth: 1
   :caption: Table of Contents:

   lexer
   grammar
   tokens
   symbol
   actions
   lltable

Key Features
------------

- **Automated Translation**: Converts `.lsf` scripts to Python scripts compatible with the Python Meep library.
- **Cross-Platform**: Works on major operating systems (Windows, macOS, Linux).
- **Extensible**: Designed with modularity to support additional features and tools.

About the Project
-----------------

LUMEX was developed as part of a Bachelor's thesis project aimed at enhancing interoperability between proprietary and open-source simulation tools. The focus is on providing researchers and engineers with an efficient tool for transitioning from Lumerical's environment to Meep using Python.

