=======
 Usage
=======

Commandline options
===================

.. autoprogram:: simtrans.cli:parser
   :prog: simtrans

Convert URDF model to VRML(OpenHRP) format
==========================================

For example, PR2 robot model can be converted as follows.

.. code-block:: bash

   $ rosrun xacro xacro.py `rospack find pr2_description`/robots/pr2.urdf.xacro > /tmp/pr2.urdf
   $ simtrans -i /tmp/pr2.urdf -o /tmp/pr2.wrl

To open the project using hrpsys-simulator.

.. code-block:: bash

   $ gnome-terminal -x openhrp-model-loader
   $ hrpsys-simulator /tmp/pr2-project.xml


Convert VRML(OpenHRP) model to SDF format
=========================================

For example, PA10 robot model can be converted as follows.

.. code-block:: bash

   $ simtrans -i /usr/local/share/OpenHRP-3.1/sample/model/PA10/pa10.main.wrl -o ~/.gazebo/models/pa10.world

To open the project using gazebo.

.. code-block:: bash

   $ gazebo ~/.gazebo/models/pa10.world
