=========
 Install
=========

First, install required binary packages:

.. code-block:: bash

   $ sudo add-apt-repository ppa:hrg/daily
   $ sudo apt-get update
   $ sudo apt-get install openhrp meshlab imagemagick python-omniorb openrtm-aist-python

Clone most recent source from github:

.. code-block:: bash

   $ git clone https://github.com/fkanehiro/simtrans.git

Next, install pip and install required package using pip:

.. code-block:: bash

   $ sudo apt-get install python-setuptools
   $ sudo easy_install pip
   $ cd simtrans
   $ sudo pip install -r requirements.txt

Finally, install simtrans:

.. code-block:: bash

   $ sudo python setup.py install


Install most recent version of gazebo (optional)
================================================

If you want to convert SDF1.5 based models (most of models for DRC tasks are SDF1.5 based), you have to install most recent version of gazebo simulator.

Please refer to following page for installation of gazebo itself:

http://gazebosim.org/tutorials?tut=install_ubuntu&cat=installation

Or refer to this page to install gazebo with DRC plugins and models:

https://bitbucket.org/osrf/drcsim/wiki/DRC/Install
