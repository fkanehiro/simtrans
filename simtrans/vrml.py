# -*- coding:utf-8 -*-

"""
Reader and writer for VRML format
"""

from . import model
import os
import sys
import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from .thirdparty import transformations as tf
import numpy
import jinja2
import CORBA
import CosNaming
import OpenHRP
from pygraph.classes.graph import graph
from pygraph.classes.digraph import digraph
from pygraph.algorithms.searching import breadth_first_search


class VRMLReader(object):
    '''
    VRML reader class
    '''
    def __init__(self):
        self._orb = CORBA.ORB_init([sys.argv[0],
                                    "-ORBInitRef",
                                    "NameService=corbaloc::localhost:2809/NameService"],
                                   CORBA.ORB_ID)
        self._loader = None
        self._ns = None
        self._joints = []
        self._links = []

    def read(self, f):
        '''
        Read vrml model data given the file path

        >>> r = VRMLReader()
        >>> m = r.read('/usr/local/share/OpenHRP-3.1/sample/model/closed-link-sample.wrl')
        '''
        self.resolveModelLoader()
        try:
            b = self._loader.loadBodyInfo(f)
        except CORBA.TRANSIENT:
            print 'unable to connect to model loader corba service (is "openhrp-model-loader" running?)'
            raise
        bm = model.BodyModel()
        self._joints = []
        self._links = []
        self._hrplinks = b._get_links()
        self._hrpshapes = b._get_shapes()
        self._hrpmaterials = b._get_materials()
        self._hrpextrajoints = b._get_extraJoints()
        root = self._hrplinks[0]
        lm = self.readLink(root)
        self._links.append(lm)
        for c in root.childIndices:
            self.readChild(root, self._hrplinks[c])
        for j in self._hrpextrajoints:
            # extra joint for closed link models
            m = model.JointModel()
            m.parent = j.link[0]
            m.child = j.link[1]
            m.name = j.name
            m.axis = j.axis
            self._joints.append(m)
        bm.links = self._links
        bm.joints = self._joints
        return bm

    def readLink(self, m):
        lm = model.LinkModel()
        lm.name = m.name
        lm.visuals = []
        for s in m.shapeIndices:
            sm = model.ShapeModel()
            sm.name = "shape-%i" % s.shapeIndex
            sm.matrix = numpy.matrix(s.transformMatrix+[0, 0, 0, 1]).reshape(4, 4)
            sdata = self._hrpshapes[s.shapeIndex]
            if sdata.primitiveType == OpenHRP.SP_MESH:
                sm.shapeType = model.ShapeModel.SP_MESH
                sm.data = model.MeshData()
                sm.data.vertex = numpy.array(sdata.vertices).reshape(len(sdata.vertices)/3, 3)
                sm.data.vertex_index = numpy.array(sdata.triangles).reshape(len(sdata.triangles)/3, 3)
            elif sdata.primitiveType == OpenHRP.SP_SPHERE:
                sm.shapeType = model.ShapeModel.SP_SPHERE
                sm.data = model.SphereData()
                sm.data.radius = sdata.primitiveParameters[0]
            elif sdata.primitiveType == OpenHRP.SP_CYLINDER:
                sm.shapeType = model.ShapeModel.SP_CYLINDER
                sm.data = model.CylinderData()
                sm.data.radius = sdata.primitiveParameters[0]
                sm.data.height = sdata.primitiveParameters[1]
            elif sdata.primitiveType == OpenHRP.SP_BOX:
                sm.shapeType = model.ShapeModel.SP_BOX
                sm.data = model.BoxData()
                sm.data.x = sdata.primitiveParameters[0]
                sm.data.y = sdata.primitiveParameters[1]
                sm.data.z = sdata.primitiveParameters[2]
            else:
                raise Exception('unsupported shape primitive: %s' % sdata.primitiveType)
            lm.visuals.append(sm)
        return lm

    def readChild(self, parent, child):
        # first convert link shape information
        lm = self.readLink(child)
        self._links.append(lm)
        # then create joint pairs
        jm = model.JointModel()
        jm.parent = parent.name
        jm.child = child.name
        jm.name = jm.parent + jm.child
        if child.jointType == 'fixed':
            jm.jointType = model.JointModel.J_FIXED
        elif child.jointType == 'rotate':
            jm.jointType = model.JointModel.J_REVOLUTE
        elif child.jointType == 'slide':
            jm.jointType = model.JointModel.J_PRISMATIC
        else:
            raise Exception('unsupported joint type: %s' % child.jointType)
        try:
            jm.limit = [child.ulimit[0], child.llimit[0]]
        except IndexError:
            pass
        jm.axis = child.jointAxis
        jm.trans = child.translation
        jm.rot = tf.quaternion_about_axis(child.rotation[3], child.rotation[0:3])
        self._joints.append(jm)
        for c in child.childIndices:
            self.readChild(child, self._hrplinks[c])

    def resolveModelLoader(self):
        nsobj = self._orb.resolve_initial_references("NameService")
        self._ns = nsobj._narrow(CosNaming.NamingContext)
        try:
            obj = self._ns.resolve([CosNaming.NameComponent("ModelLoader", "")])
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
        self._roots = []

    def write(self, mdata, fname):
        '''
        Write simulation model in VRML format

        >>> from . import urdf
        >>> r = urdf.URDFReader()
        >>> m = r.read('package://atlas_description/urdf/atlas_v3.urdf')
        >>> w = VRMLWriter()
        >>> w.write(m, '/tmp/atlas.wrl')

        >>> from . import sdf
        >>> r = sdf.SDFReader()
        >>> m = r.read('model://pr2/model.sdf')
        >>> w = VRMLWriter()
        >>> w.write(m, '/tmp/pr2.wrl')
        '''
        # first convert data structure (VRML uses tree structure)
        nmodel = {}
        for m in mdata.links:
            self._linkmap[m.name] = m
        self._roots = self.findroot(mdata)
        root = self._roots[0]
        rootlink = self._linkmap[root]
        rootjoint = model.JointModel()
        rootjoint.name = root
        rootjoint.jointType = "fixed"
        nmodel['link'] = rootlink
        nmodel['joint'] = rootjoint
        nmodel['children'] = self.convertchildren(mdata, root)
        rmodel = {}
        rmodel['children'] = [nmodel]

        # assign jointId
        jointcount = 1
        jointmap = {root: 0}
        for j in mdata.joints:
            jointmap[j.name] = jointcount
            jointcount = jointcount + 1

        # list non empty link
        links = [l.name for l in mdata.links if len(l.visuals) > 0 and l.name not in self._roots[1:]]
        # list joint with parent
        joints = [j.name for j in mdata.joints if j.child in links and j.parent not in self._roots[1:]]

        # render the data structure using template
        loader = jinja2.PackageLoader(self.__module__, 'template')
        env = jinja2.Environment(loader=loader)

        # render main vrml file
        template = env.get_template('vrml.wrl')
        with open(fname, 'w') as ofile:
            ofile.write(template.render({
                'model': rmodel,
                'body': mdata,
                'links': links,
                'joints': joints,
                'jointmap': jointmap,
                'ShapeModel': model.ShapeModel
            }))

        # render mesh vrml file for each links
        template = env.get_template('vrml-mesh.wrl')
        dirname = os.path.dirname(fname)
        for l in mdata.links:
            for v in l.visuals:
                if v.shapeType == model.ShapeModel.SP_MESH:
                    m = {}
                    m['children'] = [v.data]
                    with open(os.path.join(dirname, v.name + ".wrl"), 'w') as ofile:
                        ofile.write(template.render({
                            'name': l.name,
                            'ShapeModel': model.ShapeModel,
                            'mesh': m
                        }))

        # render openhrp project
        template = env.get_template('openhrp-project.xml')
        with open(fname.replace('.wrl', '-project.xml'), 'w') as ofile:
            ofile.write(template.render({
                'model': mdata,
                'root': root,
                'fname': fname
            }))

    def convertchildren(self, mdata, linkname):
        children = []
        for cjoint in self.findchildren(mdata, linkname):
            nmodel = {}
            nmodel['joint'] = cjoint
            nmodel['jointtype'] = self.convertjointtype(cjoint.jointType)
            try:
                nmodel['link'] = self._linkmap[cjoint.child]
            except KeyError:
                #print "warning: unable to find child link %s" % cjoint.child
                pass
            nmodel['children'] = self.convertchildren(mdata, cjoint.child)
            children.append(nmodel)
        return children

    def convertjointtype(self, t):
        if t == model.JointModel.J_FIXED:
            return "fixed"
        elif t == model.JointModel.J_REVOLUTE:
            return "rotate"
        elif t == model.JointModel.J_PRISMATIC:
            return "slide"
        elif t == model.JointModel.J_SCREW:
            return "rotate"
        else:
            raise Exception('unsupported joint type: %s' % t)

    def findroot(self, mdata):
        '''
        Find root link from parent to child relationships.
        Currently based on following simple principle:
        - Link with no parent will be the root.

        >>> from . import urdf
        >>> r = urdf.URDFReader()
        >>> m = r.read('package://atlas_description/urdf/atlas_v3.urdf')
        >>> w = VRMLWriter()
        >>> w.findroot(m)[0]
        'pelvis'
        >>> from . import sdf
        >>> r = sdf.SDFReader()
        >>> m = r.read('model://pr2/model.sdf')
        >>> w = VRMLWriter()
        >>> w.findroot(m)[0]
        'base_footprint'
        '''
        joints = {}
        for j in mdata.joints:
            try:
                joints[j.parent] = joints[j.parent] + 1
            except KeyError:
                joints[j.parent] = 1
        for j in mdata.joints:
            try:
                del joints[j.child]
            except KeyError:
                pass
        return [j[0] for j in sorted(joints.items(), key=lambda x: x[1], reverse=True)]

    def findchildren(self, mdata, linkname):
        '''
        Find child joints connected to specified link

        >>> from . import urdf
        >>> r = urdf.URDFReader()
        >>> m = r.read('package://atlas_description/urdf/atlas_v3.urdf')
        >>> w = VRMLWriter()
        >>> [c.child for c in w.findchildren(m, 'pelvis')]
        ['ltorso', 'l_uglut', 'r_uglut']
        '''
        children = []
        for j in mdata.joints:
            if j.parent == linkname:
                children.append(j)
        return children
