# -*- coding:utf-8 -*-

"""
Reader and writer for VRML format
"""

from . import model
import os
import sys
from euclid import *
import jinja2
import CORBA
import CosNaming
import OpenHRP


class VRMLReader(object):
    '''
    VRML reader class
    '''
    def __init__(self):
        self._orb = CORBA.ORB_init([sys.argv[0],
                                    "-ORBInitRef",
                                    "NameService=corbaloc::localhost:2809/NameService"],
                                   CORBA.ORB_ID)

    def read(self, f):
        self.resolveModelLoader()

    def resolveModelLoader(self):
        nsobj = orb.resolve_initial_references("NameService")
        ns = nsobj._narrow(CosNaming.NamingContext)
        try:
            obj = self.ns.resolve([CosNaming.NameComponent("ModelLoader","")])
            self._loader = obj._narrow(OpenHRP.ModelLoader)
        except CosNaming.NamingContext.NotFound:
            print "unable to resolve OpenHRP model loader on CORBA name service"
            raise

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
        rootjoint.name = "BASE"
        rootjoint.jointType = "fixed"
        nmodel['link'] = rootlink
        nmodel['joint'] = rootjoint
        nmodel['children'] = self.convertchildren(mdata, root)

        # assign jointId
        jointcount = 2
        jointmap = {"BASE": 1}
        for j in mdata.joints:
            jointmap[j.name] = jointcount
            jointcount = jointcount + 1

        # render the data structure using template
        loader = jinja2.PackageLoader('simtrans', 'template')
        env = jinja2.Environment(loader=loader)

        # render main vrml file
        template = env.get_template('vrml.wrl')
        with open(fname, 'w') as ofile:
            ofile.write(template.render({'model': nmodel, 'body': mdata, 'jointmap': jointmap}))

        # render mesh vrml file for each links
        template = env.get_template('vrml-mesh.wrl')
        dirname = os.path.dirname(fname)
        for l in mdata.links:
            if l.visual is not None:
                with open(os.path.join(dirname, l.name + ".wrl"), 'w') as ofile:
                    ofile.write(template.render({'name': l.name, 'mesh': l.visual.mesh}))

    def convertchildren(self, mdata, linkname):
        children = []
        for cjoint in self.findchildren(mdata, linkname):
            try:
                nmodel = {}
                nmodel['joint'] = cjoint
                nmodel['jointtype'] = self.convertjointtype(cjoint.jointType)
                nmodel['link'] = nlink = self._linkmap[cjoint.child]
                nmodel['children'] = self.convertchildren(mdata, nlink.name)
                children.append(nmodel)
            except KeyError:
                # print "warning: unable to find child link %s" % cjoint.child
                pass
        return children

    def convertjointtype(self, t):
        if t == model.JointModel.J_FIXED:
            return "fixed"
        elif t == model.JointModel.J_REVOLUTE:
            return "rotate"

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
