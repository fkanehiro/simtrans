Architecture
============

Software architecture of simtrans is shown below.
Reader and writer for each formats will read and write the common data structure.
 
.. graphviz::
 
   digraph comp {
     rankdir=LR;
     "SDLReader" -> "Model"
     "URDFReader" -> "Model"
     "VRMLReader" -> "Model"
     "STLReader" -> "Model"
     "ColladaReader" -> "Model"
     "Model" -> "SDLWriter";
     "Model" -> "URDFWriter";
     "Model" -> "VRMLWriter";
     "Model" -> "STLWriter";
     "Model" -> "ColladaWriter";
   }

Common data structure
=====================

simtrans.model
--------------

.. automodule:: simtrans.model
    :members:
    :undoc-members:
    :show-inheritance:

Command-line interface
======================

simtrans.cli
------------

.. automodule:: simtrans.cli
    :members:
    :undoc-members:
    :show-inheritance:

simtrans.catxml
---------------

.. automodule:: simtrans.catxml
    :members:
    :undoc-members:
    :show-inheritance:

simtrans.gzfetch
----------------

.. automodule:: simtrans.gzfetch
    :members:
    :undoc-members:
    :show-inheritance:

Reader and writer
=================

simtrans.collada
----------------

.. automodule:: simtrans.collada
    :members:
    :undoc-members:
    :show-inheritance:

simtrans.graphviz
-----------------

.. automodule:: simtrans.graphviz
    :members:
    :undoc-members:
    :show-inheritance:

simtrans.sdf
------------

.. automodule:: simtrans.sdf
    :members:
    :undoc-members:
    :show-inheritance:

simtrans.stl
------------

.. automodule:: simtrans.stl
    :members:
    :undoc-members:
    :show-inheritance:

simtrans.urdf
-------------

.. automodule:: simtrans.urdf
    :members:
    :undoc-members:
    :show-inheritance:

simtrans.vrml
-------------

.. automodule:: simtrans.vrml
    :members:
    :undoc-members:
    :show-inheritance:

Utility functions
=================

simtrans.utils
--------------

.. automodule:: simtrans.utils
    :members:
    :undoc-members:
    :show-inheritance:

Thirdparty library
==================

.. toctree::

    simtrans.thirdparty

