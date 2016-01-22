=======
 Usage
=======

Commandline options
===================

.. autoprogram:: simtrans.cli:parser
   :prog: simtrans

.. autoprogram:: simtrans.cli:checkerparser
   :prog: simtrans-checker


Convert URDF model to VRML format
=================================

For example, PR2 robot model can be converted as follows.

.. code-block:: bash

   $ rosrun xacro xacro.py `rospack find pr2_description`/robots/pr2.urdf.xacro > /tmp/pr2.urdf
   $ simtrans -i /tmp/pr2.urdf -o /tmp/pr2.wrl

To open the project using hrpsys-simulator.

.. code-block:: bash

   $ gnome-terminal -x openhrp-model-loader
   $ hrpsys-simulator /tmp/pr2-project.xml


Convert VRML model to SDF format
================================

For example, PA10 robot model can be converted as follows.

.. code-block:: bash

   $ simtrans -i /usr/local/share/OpenHRP-3.1/sample/model/PA10/pa10.main.wrl -o ~/.gazebo/models/pa10.world

To open the project using gazebo.

.. code-block:: bash

   $ gazebo ~/.gazebo/models/pa10.world


Validate all the models in the folder
=====================================

For example, we can check JVRC task models as follows.

.. code-block:: bash

   $ git clone https://github.com/jvrc/model.git jvrcmodels
   $ simtrans-checker jvrcmodels/tasks/*/*.wrl


Visualize joint structure using graphviz
========================================

For example, PR2 robot model can be visualized as follows.

.. code-block:: bash

   $ rosrun xacro xacro.py `rospack find pr2_description`/robots/pr2.urdf.xacro > /tmp/pr2.urdf
   $ simtrans -i /tmp/pr2.urdf -o /tmp/pr2.dot
   $ dot -Tx11 /tmp/pr2.dot
