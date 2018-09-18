# -*- coding:utf-8 -*-

"""Writer for graphviz dot format

:Organization:
 MID

Examples
--------

Write simulation model in graphviz dot format

>>> import subprocess
>>> subprocess.call('rosrun xacro xacro.py `rospack find atlas_description`/robots/atlas_v3.urdf.xacro > /tmp/atlas.urdf', shell=True)
0
>>> from . import urdf
>>> r = urdf.URDFReader()
>>> m = r.read('/tmp/atlas.urdf')
>>> w = GraphvizWriter()
>>> w.write(m, '/tmp/atlas.dot')

>>> from . import sdf
>>> r = sdf.SDFReader()
>>> m = r.read('model://pr2/model.sdf')
>>> w = GraphvizWriter()
>>> w.write(m, '/tmp/pr2.dot')

>>> import os
>>> from . import vrml
>>> r = vrml.VRMLReader()
>>> m = r.read(os.path.expandvars('$OPENHRP_MODEL_PATH/PA10/pa10.main.wrl'))
>>> w = GraphvizWriter()
>>> w.write(m, '/tmp/pa10.dot')
"""

class GraphvizWriter(object):
    '''
    Graphviz writer class
    '''
    def __init__(self):
        self._linkmap = {}

    def write(self, mdata, fname, options=None):
        '''
        Write simulation model in graphviz dot format
        '''
        with open(fname, 'w') as f:
            f.write("digraph model {\n")
            for j in mdata.joints:
                f.write('   %s -> %s [label="%s"]\n' % (j.parent, j.child, j.name))
            f.write("}\n")
