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
import copy
import jinja2
try:
    import CORBA
    import CosNaming
    import OpenHRP
except ImportError:
    print "Unable to find CORBA and OpenHRP library."
    print "You can install the library by:"
    print "$ sudo add-apt-repository ppa:hrg/daily"
    print "$ sudo apt-get update"
    print "$ sudo apt-get install openhrp openrtm-aist-python"
    raise

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
        bm.trans = numpy.array(root.translation)
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
            m.parent = j.link[0] + '_LINK'
            m.child = j.link[1] + '_LINK'
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
        lm.name = m.name + '_LINK'
        lm.mass = m.mass
        lm.centerofmass = numpy.array(m.centerOfMass)
        lm.inertia = numpy.array(m.inertia).reshape(3, 3)
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
                sm.data = self.readMesh(sdata)
            elif sdata.primitiveType == OpenHRP.SP_SPHERE and numpy.allclose(sm.matrix, numpy.identity(4)):
                sm.shapeType = model.ShapeModel.SP_SPHERE
                sm.data = model.SphereData()
                sm.data.radius = sdata.primitiveParameters[0]
                sm.data.material = self._materials[sdata.appearanceIndex]
            elif sdata.primitiveType == OpenHRP.SP_CYLINDER and numpy.allclose(sm.matrix, numpy.identity(4)):
                sm.shapeType = model.ShapeModel.SP_CYLINDER
                sm.data = model.CylinderData()
                sm.data.radius = sdata.primitiveParameters[0]
                sm.data.height = sdata.primitiveParameters[1]
                sm.data.material = self._materials[sdata.appearanceIndex]
            elif sdata.primitiveType == OpenHRP.SP_BOX and numpy.allclose(sm.matrix, numpy.identity(4)):
                sm.shapeType = model.ShapeModel.SP_BOX
                sm.data = model.BoxData()
                sm.data.x = sdata.primitiveParameters[0]
                sm.data.y = sdata.primitiveParameters[1]
                sm.data.z = sdata.primitiveParameters[2]
                sm.data.material = self._materials[sdata.appearanceIndex]
            else:
                # raise Exception('unsupported shape primitive: %s' % sdata.primitiveType)
                sm.shapeType = model.ShapeModel.SP_MESH
                sm.data = self.readMesh(sdata)
            lm.visuals.append(sm)
        return lm

    def readMesh(self, sdata):
        data = model.MeshData()
        data.vertex = numpy.array(sdata.vertices).reshape(len(sdata.vertices)/3, 3)
        data.vertex_index = numpy.array(sdata.triangles).reshape(len(sdata.triangles)/3, 3)
        adata = self._hrpapperances[sdata.appearanceIndex]
        if adata.normalPerVertex is True:
            data.normal = numpy.array(adata.normals).reshape(len(adata.normals)/3, 3)
            if len(adata.normalIndices) > 0:
                data.normal_index = numpy.array(adata.normalIndices).reshape(len(adata.normalIndices)/3, 3)
            else:
                data.normal_index = data.vertex_index
        else:
            data.normal = numpy.array(adata.normals).reshape(len(adata.normals)/3, 3)
            if len(adata.normalIndices) > 0:
                idx = []
                for i in adata.normalIndices:
                    idx.append(i)
                    idx.append(i)
                    idx.append(i)
                data.normal_index = numpy.array(idx).reshape(len(idx)/3, 3)
            else:
                idx = []
                for i in range(0, len(adata.normals)/3):
                    idx.append(i)
                    idx.append(i)
                    idx.append(i)
                data.normal_index = numpy.array(idx).reshape(len(idx)/3, 3)
        if len(data.vertex_index) != len(data.normal_index):
            raise Exception('vertex length and normal length not match')
        data.material = self._materials[adata.materialIndex]
        if adata.textureIndex >= 0:
            fname = self._hrptextures[adata.textureIndex].url
            if self._assethandler:
                data.material.texture = self._assethandler(fname)
            else:
                data.material.texture = fname
            data.uvmap = numpy.array(adata.textureCoordinate).reshape(len(adata.textureCoordinate)/2, 2)
            data.uvmap_index = numpy.array(adata.textureCoordIndices).reshape(len(adata.textureCoordIndices)/3, 3)
        return data

    def readChild(self, parent, child):
        # first, create joint pairs
        jm = model.JointModel()
        if parent.name != 'world':
            jm.parent = parent.name + '_LINK'
        else:
            jm.parent = parent.name
        jm.child = child.name + '_LINK'
        jm.name = child.name
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
        # convert to absolute position
        if isinstance(parent, model.JointModel):
            pm = parent
        else:
            pm = model.JointModel()
            pm.trans = numpy.array(parent.translation)
            pm.rot = tf.quaternion_about_axis(parent.rotation[3], parent.rotation[0:3])
        jm.matrix = numpy.dot(pm.getmatrix(), jm.getmatrix())
        jm.trans = None
        jm.rot = None
        self._joints.append(jm)
        # then, convert link shape information
        lm = self.readLink(child)
        lm.matrix = jm.getmatrix()
        lm.trans = None
        lm.rot = None
        self._links.append(lm)
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
        self._ignore = []

    def write(self, mdata, fname):
        '''
        Write simulation model in VRML format
        '''
        fpath, fext = os.path.splitext(fname)
        basename = os.path.basename(fpath)
        dirname = os.path.dirname(fname)
        if mdata.name is None or mdata.name == '':
            mdata.name = basename

        # find root joint (including local peaks)
        self._roots = utils.findroot(mdata)

        # render the data structure using template
        loader = jinja2.PackageLoader(self.__module__, 'template')
        env = jinja2.Environment(loader=loader, extensions=['jinja2.ext.do'])

        self._linkmap['world'] = model.LinkModel()
        for m in mdata.links:
            self._linkmap[m.name] = m

        # render main vrml file for each bodies
        template = env.get_template('vrml.wrl')
        modelfiles = {}
        for root in self._roots:
            # first convert data structure (VRML uses tree structure)
            if root == 'world':
                roots = utils.findchildren(mdata, root)
                for r in roots:
                    # print("root joint is world. using %s as root" % root)
                    mfname = os.path.join(dirname, mdata.name + "-" + r.child + ".wrl")
                    self.renderchildren(mdata, r.child, "fixed", mfname, template)
                    modelfiles[mfname] = self._linkmap[r.child]
            else:
                mfname = os.path.join(dirname, mdata.name + "-" + root + ".wrl")
                self.renderchildren(mdata, root, "free", mfname, template)
                modelfiles[os.path.basename(mfname)] = self._linkmap[root]
        
        # render mesh vrml file for each links
        template = env.get_template('vrml-mesh.wrl')
        for l in mdata.links:
            for v in l.visuals:
                if v.shapeType == model.ShapeModel.SP_MESH:
                    v.data.pretranslate()
                    m = {}
                    m['children'] = [v.data]
                    with open(os.path.join(dirname, mdata.name + "-" + l.name + "-" + v.name + ".wrl"), 'w') as ofile:
                        ofile.write(template.render({
                            'name': v.name,
                            'ShapeModel': model.ShapeModel,
                            'mesh': m
                        }))

        # render openhrp project
        template = env.get_template('openhrp-project.xml')
        with open(fname.replace('.wrl', '-project.xml'), 'w') as ofile:
            ofile.write(template.render({
                'models': modelfiles,
            }))

        # render choreonoid project
        template = env.get_template('choreonoid-project.yaml')
        with open(fname.replace('.wrl', '-project.cnoid'), 'w') as ofile:
            ofile.write(template.render({
                'models': modelfiles,
            }))

    def convertchildren(self, mdata, pjoint, joints, links):
        children = []
        plink = self._linkmap[pjoint.child]
        for cjoint in utils.findchildren(mdata, pjoint.child):
            nmodel = {}
            try:
                clink = self._linkmap[cjoint.child]
            except KeyError:
                print "warning: unable to find child link %s" % cjoint.child
            (cchildren, joints, links) = self.convertchildren(mdata, cjoint, joints, links)
            pjointinv = numpy.linalg.pinv(pjoint.getmatrix())
            cjointinv = numpy.linalg.pinv(cjoint.getmatrix())
            cjoint2 = copy.deepcopy(cjoint)
            cjoint2.matrix = numpy.dot(cjoint.getmatrix(), pjointinv)
            cjoint2.trans = None
            cjoint2.rot = None
            clink2 = copy.deepcopy(clink)
            clink2.matrix = numpy.dot(clink.getmatrix(), cjointinv)
            clink2.trans = None
            clink2.rot = None
            if clink2.mass == 0:
                print "[warning] detect link with mass zero, assigning small (0.001) mass."
                clink2.mass = 0.001
            if not numpy.allclose(clink2.getmatrix(), numpy.identity(4)):
                clink2.translate(clink2.getmatrix())
            nmodel['joint'] = cjoint2
            nmodel['jointtype'] = self.convertjointtype(cjoint.jointType)
            nmodel['link'] = clink2
            nmodel['children'] = cchildren
            children.append(nmodel)
            joints.append(cjoint.name)
            links.append(cjoint.child)
        return (children, joints, links)

    def renderchildren(self, mdata, root, jointtype, fname, template):
        nmodel = {}
        rootlink = self._linkmap[root]
        rootjoint = model.JointModel()
        rootjoint.name = root
        rootjoint.jointType = jointtype
        rootjoint.matrix = rootlink.getmatrix()
        rootjoint.trans = None
        rootjoint.rot = None
        rootjoint.child = root
        (children, joints, links) = self.convertchildren(mdata, rootjoint, [], [])
        nmodel['link'] = rootlink
        nmodel['joint'] = rootjoint
        nmodel['jointtype'] = rootjoint.jointType
        nmodel['children'] = children

        # assign jointId
        jointmap = {root: 0}
        for j in joints:
            jointmap[j] = 0
        jointcount = 1
        for j in joints:
            jointmap[j] = jointcount
            jointcount = jointcount + 1

        with open(fname, 'w') as ofile:
            ofile.write(template.render({
                'model': {'name':rootlink.name, 'children':[nmodel]},
                'body': mdata,
                'links': links,
                'joints': joints,
                'jointmap': jointmap,
                'ShapeModel': model.ShapeModel
            }))

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
