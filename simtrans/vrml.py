# -*- coding:utf-8 -*-

"""Reader and writer for VRML format

:Organization:
 AIST

Requirements
------------
* numpy
* omniorb-python
* jinja2 template engine

Examples
--------

Read vrml model data given the file path

>>> r = VRMLReader()
>>> m = r.read('/usr/local/share/OpenHRP-3.1/sample/model/closed-link-sample.wrl')

Write simulation model in URDF format

>>> from . import vrml
>>> r = vrml.VRMLReader()
>>> m = r.read('/home/yosuke/HRP-4C/HRP4Cmain.wrl')
>>> w = URDFWriter()
>>> w.write(m, '/tmp/hrp4c.urdf')
>>> import subprocess
>>> subprocess.check_call('check_urdf /tmp/hrp4c.urdf'.split(' '))
0

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
"""

from . import model
from . import utils
import os
import sys
import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from .thirdparty import transformations as tf
import math
import numpy
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
        self._loader = None
        self._ns = None
        self._model = None
        self._joints = []
        self._links = []
        self._materials = []
        self._sensors = []
        self._assethandler = None

    def read(self, f, assethandler=None):
        '''
        Read vrml model data given the file path
        '''
        self._assethandler = assethandler
        self.resolveModelLoader()
        try:
            self._model = self._loader.loadBodyInfo(f)
        except CORBA.TRANSIENT:
            print 'unable to connect to model loader corba service (is "openhrp-model-loader" running?)'
            raise
        bm = model.BodyModel()
        self._joints = []
        self._links = []
        self._materials = []
        self._sensors = []
        self._hrplinks = self._model._get_links()
        self._hrpshapes = self._model._get_shapes()
        self._hrpapperances = self._model._get_appearances()
        self._hrpmaterials = self._model._get_materials()
        self._hrptextures = self._model._get_textures()
        self._hrpextrajoints = self._model._get_extraJoints()
        mid = 0
        for a in self._hrpmaterials:
            m = model.MaterialModel()
            m.name = "material-%i" % mid
            mid = mid + 1
            m.ambient = a.ambientIntensity
            m.diffuse = a.diffuseColor + [1.0]
            m.specular = a.specularColor + [1.0]
            m.emission = a.emissiveColor + [1.0]
            m.shininess = a.shininess
            m.transparency = a.transparency
            self._materials.append(m)
        root = self._hrplinks[0]
        if root.jointType == 'fixed':
            world = model.JointModel()
            world.name = 'world'
            self.readChild(world, root)
        else:
            lm = self.readLink(root)
            self._links.append(lm)
            for c in root.childIndices:
                self.readChild(root, self._hrplinks[c])
        for j in self._hrpextrajoints:
            # extra joint for closed link models
            m = model.JointModel()
            m.jointType = model.JointModel.J_REVOLUTE
            m.parent = j.link[0]
            m.child = j.link[1]
            m.name = j.name
            m.axis = numpy.array(j.axis)
            m.trans = numpy.array(j.point[1])
            m.offsetPosition = True
            self._joints.append(m)
        bm.links = self._links
        bm.joints = self._joints
        bm.sensors = self._sensors
        return bm

    def readLink(self, m):
        lm = model.LinkModel()
        lm.name = m.name
        lm.mass = m.mass
        lm.centerofmass = numpy.array(m.centerOfMass)
        lm.visuals = []
        for s in m.sensors:
            sm = model.SensorModel()
            sm.name = s.name
            sm.parent = lm.name
            sm.trans = numpy.array(s.translation)
            # sensors in OpenHRP is defined based on Z-axis up. so we
            # will rotate them to X-axis up here.
            # see http://www.openrtp.jp/openhrp3/jp/create_model.html
            rot = tf.quaternion_multiply(tf.quaternion_about_axis(s.rotation[3], s.rotation[0:3]), tf.quaternion_about_axis(-math.pi/2, [0, 0, 1]))
            sm.rot = tf.quaternion_multiply(rot, tf.quaternion_about_axis(math.pi/2, [0, 1, 0]))
            if s.type == 'Vision':
                sm.sensorType = model.SensorModel.SS_CAMERA
                sm.data = model.CameraData()
                sm.data.near = s.specValues[0]
                sm.data.far = s.specValues[1]
                sm.data.fov = s.specValues[2]
                if s.specValues[3] == 1:
                    sm.data.cameraType = model.CameraData.CS_COLOR
                elif s.specValues[3] == 2:
                    sm.data.cameraType = model.CameraData.CS_MONO
                elif s.specValues[3] == 3:
                    sm.data.cameraType = model.CameraData.CS_DEPTH
                else:
                    raise Exception('unsupported camera type: %i' % s.specValues[3])
                sm.data.width = s.specValues[4]
                sm.data.height = s.specValues[5]
                sm.rate = s.specValues[6]
            elif s.type == 'Range':
                sm.sensorType = model.SensorModel.SS_RAY
                sm.data = model.RayData()
                (scanangle, scanstep, scanrate, maxdistance) = s.specValues
                sm.data.min_angle = - scanangle / 2
                sm.data.max_angle = scanangle / 2
                sm.data.min_range = 0.08
                sm.data.max_range = maxdistance
                sm.rate = scanrate
            self._sensors.append(sm)
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
                adata = self._hrpapperances[sdata.appearanceIndex]
                if adata.normalPerVertex is True:
                    sm.data.normal = numpy.array(adata.normals).reshape(len(adata.normals)/3, 3)
                    if len(adata.normalIndices) > 0:
                        sm.data.normal_index = numpy.array(adata.normalIndices).reshape(len(adata.normalIndices)/3, 3)
                    else:
                        sm.data.normal_index = sm.data.vertex_index
                else:
                    sm.data.normal = numpy.array(adata.normals).reshape(len(adata.normals)/3, 3)
                    if len(adata.normalIndices) > 0:
                        idx = []
                        for i in adata.normalIndices:
                            idx.append(i)
                            idx.append(i)
                            idx.append(i)
                        sm.data.normal_index = numpy.array(idx).reshape(len(idx)/3, 3)
                    else:
                        idx = []
                        for i in range(0, len(adata.normals)/3):
                            idx.append(i)
                            idx.append(i)
                            idx.append(i)
                        sm.data.normal_index = numpy.array(idx).reshape(len(idx)/3, 3)
                if len(sm.data.vertex_index) != len(sm.data.normal_index):
                    raise Exception('vertex length and normal length not match in %s' % sm.name)
                sm.data.material = self._materials[adata.materialIndex]
                if adata.textureIndex >= 0:
                    fname = self._hrptextures[adata.textureIndex].url
                    if self._assethandler:
                        sm.data.material.texture = self._assethandler(fname)
                    else:
                        sm.data.material.texture = fname
                    sm.data.uvmap = numpy.array(adata.textureCoordinate).reshape(len(adata.textureCoordinate)/2, 2)
                    sm.data.uvmap_index = numpy.array(adata.textureCoordIndices).reshape(len(adata.textureCoordIndices)/3, 3)
            elif sdata.primitiveType == OpenHRP.SP_SPHERE:
                sm.shapeType = model.ShapeModel.SP_SPHERE
                sm.data = model.SphereData()
                sm.data.radius = sdata.primitiveParameters[0]
                sm.data.material = self._materials[sdata.appearanceIndex]
            elif sdata.primitiveType == OpenHRP.SP_CYLINDER:
                sm.shapeType = model.ShapeModel.SP_CYLINDER
                sm.data = model.CylinderData()
                sm.data.radius = sdata.primitiveParameters[0]
                sm.data.height = sdata.primitiveParameters[1]
                sm.data.material = self._materials[sdata.appearanceIndex]
            elif sdata.primitiveType == OpenHRP.SP_BOX:
                sm.shapeType = model.ShapeModel.SP_BOX
                sm.data = model.BoxData()
                sm.data.x = sdata.primitiveParameters[0]
                sm.data.y = sdata.primitiveParameters[1]
                sm.data.z = sdata.primitiveParameters[2]
                sm.data.material = self._materials[sdata.appearanceIndex]
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
        try:
            jm.velocitylimit = [child.uvlimit[0], child.lvlimit[0]]
        except IndexError:
            pass
        jm.axis = child.jointAxis
        jm.trans = numpy.array(child.translation)
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
        '''
        fpath, fext = os.path.splitext(fname)
        basename = os.path.basename(fpath)
        if mdata.name is None or mdata.name == '':
            mdata.name = basename

        # list non empty link
        links = [l.name for l in mdata.links if len(l.visuals) > 0 and l.name not in self._roots[1:]]
        # list joint with parent
        joints = [j.name for j in mdata.joints if j.child in links and j.parent not in self._roots[1:]]

        # first convert data structure (VRML uses tree structure)
        nmodel = {}
        self._linkmap['world'] = model.LinkModel()
        for m in mdata.links:
            self._linkmap[m.name] = m
        self._roots = utils.findroot(mdata)
        if len(self._roots) > 0:
            root = self._roots[0]
            rootlink = self._linkmap[root]
            rootjoint = model.JointModel()
            rootjoint.name = root
            rootjoint.jointType = "fixed"
        else:
            if len(joints) > 0:
                root = joints[0]
            else:
                root = 'waist'
            rootlink = mdata.links[0]
            rootjoint = model.JointModel()
            rootjoint.name = root
            rootjoint.jointType = "fixed"

        if len(joints) == 0:
            joints = [root]

        nmodel['link'] = rootlink
        nmodel['joint'] = rootjoint
        nmodel['jointtype'] = rootjoint.jointType
        nmodel['children'] = self.convertchildren(mdata, root)
        rmodel = {}
        rmodel['children'] = [nmodel]

        # assign jointId
        jointmap = {root: 0}
        for j in mdata.joints:
            jointmap[j.name] = 0
        jointcount = 1
        for j in mdata.joints:
            jointmap[j.name] = jointcount
            jointcount = jointcount + 1

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
                    with open(os.path.join(dirname, mdata.name + "-" + v.name + ".wrl"), 'w') as ofile:
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
        for cjoint in utils.findchildren(mdata, linkname):
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
        elif t == model.JointModel.J_CONTINUOUS:
            return "rotate"
        else:
            raise Exception('unsupported joint type: %s' % t)
