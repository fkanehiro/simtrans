=========
 Install
=========

First, install required binary packages:

.. code-block:: bash

   $ sudo add-apt-repository ppa:hrg/ppa
   $ sudo apt-get install openhrp3 meshlab imagemagick omniorb-python

Clone most recent source from github:

.. code-block:: bash

   $ git clone https://github.com/fkanehiro/simtrans.git

Next, install pip and install required package using pip:

.. code-block:: bash

   $ sudo easy_install pip
   $ cd simtrans
   $ sudo pip install -r requirements.txt

Finally, install simtrans:

.. code-block:: bash

   $ sudo python setup.py install
