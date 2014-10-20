# -*- coding:utf-8 -*-

"""
Reader and writer for VRML format
"""

from . import model
import os
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
    def __init__(self):
        self._linkmap = {}

    def write(self, mdata, fname):
        '''
        Write simulation model in VRML format

        >>> from . import urdf
        >>> r = urdf.URDFReader()
        >>> m = r.read('/opt/ros/indigo/share/atlas_description/urdf/atlas_v3.urdf')
        >>> w = VRMLWriter()
        >>> w.write(m, '/tmp/test.wrl')
        '''
        # first convert data structure (VRML uses tree structure)
        nmodel = {}
        for m in mdata.links:
            self._linkmap[m.name] = m
        root = self.findroot(mdata)[0]
        rootlink = self._linkmap[root]
        rootjoint = model.JointModel()
        rootjoint.name = root
        rootjoint.jointType = "fixed"
        nmodel['link'] = rootlink
        nmodel['joint'] = rootjoint
        nmodel['children'] = self.convertchildren(mdata, root)

        # render the data structure using template
        loader = jinja2.PackageLoader('simtrans', 'template')
        env = jinja2.Environment(loader=loader)

        # render main vrml file
        template = env.get_template('vrml.wrl')
        with open(fname, 'w') as ofile:
            ofile.write(template.render({'model': nmodel, 'body': mdata}))

        # render mesh vrml file for each links
        template = env.get_template('vrml-mesh.wrl')
        dirname = os.path.dirname(fname)
        for l in mdata.links:
            if l.visual is not None:
                with open(os.path.join(dirname, l.name + ".wrl"), 'w') as ofile:
                    ofile.write(template.render({'mesh': l.visual.mesh}))

    def convertchildren(self, mdata, linkname):
        children = []
        for cjoint in self.findchildren(mdata, linkname):
            try:
                nmodel = {}
                nmodel['joint'] = cjoint
                nmodel['link'] = nlink = self._linkmap[cjoint.child]
                nmodel['children'] = self.convertchildren(mdata, nlink.name)
                children.append(nmodel)
            except KeyError:
                # print "warning: unable to find child link %s" % cjoint.child
                pass
        return children

    def findroot(self, mdata):
        '''
        Find root link from parent to child relationships.
        Currently based on following simple principle:
        - Link with no parent will be the root.

        >>> from . import urdf
        >>> r = urdf.URDFReader()
        >>> m = r.read('/opt/ros/indigo/share/atlas_description/urdf/atlas_v3.urdf')
        >>> w = VRMLWriter()
        >>> w.findroot(m)
        ['pelvis']
        '''
        joints = {}
        for j in mdata.joints:
            joints[j.parent] = 1
        for j in mdata.joints:
            try:
                del joints[j.child]
            except KeyError:
                pass
        return joints.keys()

    def findchildren(self, mdata, linkname):
        '''
        Find child joints connected to specified link

        >>> from . import urdf
        >>> r = urdf.URDFReader()
        >>> m = r.read('/opt/ros/indigo/share/atlas_description/urdf/atlas_v3.urdf')
        >>> w = VRMLWriter()
        >>> [c.child for c in w.findchildren(m, 'pelvis')]
        ['ltorso', 'l_uglut', 'r_uglut']
        '''
        children = []
        for j in mdata.joints:
            if j.parent == linkname:
                children.append(j)
        return children
