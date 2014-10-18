# -*- coding:utf-8 -*-

"""
Reader and writer for VRML format
"""

import jinja2


class VRMLReader(object):
    '''
    VRML reader class
    '''
    def read(self, f):
        pass


class VRMLWriter(object):
    '''
    VRML writer class
    '''
    def write(self, mdata, fname):
        '''
        >>> from . import urdf
        >>> r = urdf.URDFReader()
        >>> mdata = r.read('/opt/ros/indigo/share/atlas_description/urdf/atlas_v3.urdf')
        >>> w = VRMLWriter()
        >>> w.write(mdata, 'test.wrl')
        '''
        env = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))
        template = env.get_template('vrml.wrl')
        ofile = open(fname, 'w')
        ofile.write(template.render(mdata))

    def findroot(self, mdata):
        '''
        Find a root link from the parent to child relationships.
        Currently based on following simple rule:
        - Link with no parent will be the root.
        '''
        joints = {}
        for j in mdata.joints:
            joints[j.parent] = 1
        for j in mdata.joints:
            try:
                del joints[j.child]
            except KeyError:
                pass
