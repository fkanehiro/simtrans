# -*- coding:utf-8 -*-
# pylint: disable=too-few-public-methods, line-too-long

"""
Common data structure for model converter
"""

from __future__ import absolute_import
import logging
import numpy
import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from .thirdparty import transformations as tf
from .thirdparty import hrputil as hrputil


class ProjectModel(object):
    """
    Project model
    """
    name = None        #: Name of the simulation
    bodies = []        #: List of body models

    def __init__(self):
        self.bodies = []


class TransformationModel(object):
    """
    Transformation model with utility methods

    Used as a base class for each models

    >>> m = TransformationModel()
    >>> numpy.allclose(m.gettranslation(), [0, 0, 0])
    True
    >>> numpy.allclose(m.getscale(), [1, 1, 1])
    True
    >>> numpy.allclose(m.getrpy(), [0, 0, 0])
    True
    >>> numpy.allclose(m.getangle()[0], [0, 1, 0])
    True
    >>> numpy.allclose(m.getangle()[1], 0)
    True
    """
    matrix = None     #: Transformation matrix (4x4 numpy matrix)
    trans = None      #: Translation vector (3-dim numpy array)
    scale = None      #: Scale vector (3-dim numpy array)
    rot = None        #: Rotation (4-dim numpy array in quaternion representation)

    def __init__(self):
        self.matrix = None
        self.trans = numpy.array([0, 0, 0])
        self.scale = numpy.array([1, 1, 1])
        self.rot = numpy.array([1, 0, 0, 0])

    def isvalid(self):
        valid = True
        allnone = True
        if self.matrix is not None:
            if True in numpy.isnan(self.matrix):
                logging.error('NaN in the transformation matrix')
                valid = False
            allnone = False
        if self.trans is not None:
            if True in numpy.isnan(self.trans):
                logging.error('NaN in the translation vector')
                valid = False
            allnone = False
        if self.scale is not None:
            if True in numpy.isnan(self.scale):
                logging.error('NaN in the scale vector')
                valid = False
            allnone = False
        if self.rot is not None:
            if True in numpy.isnan(self.rot):
                logging.error('NaN in the rotation vector')
                valid = False
            allnone = False
        if allnone:
            logging.error('no transformation data in the model')
            valid = False
        return valid

    def gettranslation(self):
        if self.matrix is not None:
            translation, scale, axis = hrputil.decomposeMatrix(self.matrix)
            return translation
        else:
            return self.trans

    def getscale(self):
        if self.matrix is not None:
            transform, scale, axis = hrputil.decomposeMatrix(self.matrix)
            return scale
        else:
            return self.scale

    def getrotation(self):
        if self.matrix is not None:
            transform, scale, axis = hrputil.decomposeMatrix(self.matrix)
            m = tf.quaternion_matrix(tf.quaternion_about_axis(axis[1], axis[0]))
            return tf.quaternion_from_matrix(m)
        else:
            return self.rot

    def getrpy(self):
        if self.matrix is not None:
            transform, scale, axis = hrputil.decomposeMatrix(self.matrix)
            m = tf.quaternion_matrix(tf.quaternion_about_axis(axis[1], axis[0]))
            return tf.euler_from_matrix(m)
        else:
            return tf.euler_from_quaternion(self.rot)

    def getangle(self):
        if self.matrix is not None:
            transform, scale, axis = hrputil.decomposeMatrix(self.matrix)
            return axis
        else:
            m = tf.quaternion_matrix(self.rot)
            transform, scale, axis = hrputil.decomposeMatrix(m)
            return axis

    def getmatrix(self):
        if self.matrix is not None:
            return self.matrix
        else:
            M = numpy.identity(4)
            if self.trans is not None:
                T = numpy.identity(4)
                T[:3, 3] = self.trans[:3]
                M = numpy.dot(M, T)
            if self.rot is not None:
                R = tf.quaternion_matrix(self.rot)
                M = numpy.dot(M, R)
            if self.scale is not None:
                S = numpy.identity(4)
                S[0, 0] = self.scale[0]
                S[1, 1] = self.scale[1]
                S[2, 2] = self.scale[2]
                M = numpy.dot(M, S)
            M /= M[3, 3]
            return M

    def setmatrix(self, m):
        self.matrix = m
        self.trans = None
        self.rot = None
        self.scale = None


class BodyModel(TransformationModel):
    """
    Body model
    """
    name = None        #: Name of the body
    links = []         #: List of links
    joints = []        #: List of joints
    sensors = []       #: List of sensors
    materials = []     #: List of materials

    def __init__(self):
        TransformationModel.__init__(self)
        self.links = []
        self.joints = []
        self.sensors = []
        self.materials = []

    def isvalid(self):
        valid = TransformationModel.isvalid(self)
        linknames = {}
        jointnames = {}
        jointids = {}
        for l in self.links:
            if l.name in linknames:
                logging.warn('found overlapping link name: %s', l.name)
            linknames[l.name] = True
            valid = valid and l.isvalid()
        for j in self.joints:
            if j.name in jointnames:
                logging.warn('found overlapping joint name: %s', j.name)
            jointnames[j.name] = True
            if j.jointId != -1 and j.jointId in jointids:
                logging.warn('found overlapping joint ID: %i', j.jointId)
            jointids[j.jointId] = True
            valid = valid and j.isvalid()
        return valid


class LinkModel(TransformationModel):
    """
    Link model
    """
    name = None          #: Name of the link
    mass = 0             #: Mass of the link
    centerofmass = None  #: Center of mass (3-dim array)
    inertia = None       #: Inertia (3x3 numpy matrix)
    visuals = []         #: List of shape information used for rendering
    collisions = []      #: List of shape information used for collision detection

    def __init__(self):
        TransformationModel.__init__(self)
        self.centerofmass = [0, 0, 0]
        self.inertia = numpy.identity(3)

    def isvalid(self):
        valid = TransformationModel.isvalid(self)
        if self.name is not None:
            logging.info('validating link %s', self.name)
        else:
            logging.error('link name not set')
            valid = False
        if self.mass == 0:
            logging.warn('mass is zero')
        elif self.mass < 0:
            logging.error('mass is minus')
            valid = False
        if True in numpy.isnan(self.centerofmass):
            logging.error('NaN in the center of mass vector')
            valid = False
        if True in numpy.isinf(self.centerofmass):
            logging.error('Inf in the center of mass vector')
            valid = False
        if self.inertia.shape != (3, 3):
            logging.error('shape of the inertia matrix is not 3x3')
            valid = False
        if True in numpy.isnan(self.inertia):
            logging.error('NaN in the inertia matrix')
            valid = False
        if True in numpy.isinf(self.inertia):
            logging.error('Inf in the inertia matrix')
            valid = False
        if numpy.allclose(self.inertia, self.inertia.transpose()) == False:
            logging.error('the inertia matrix is not diagonal')
            #valid = False
        for s in self.visuals + self.collisions:
            valid = valid and s.isvalid()
        # calc bounding box from all the shapes
        allbb = self.getbbox()
        logging.debug('unified bounding box: %s', str(allbb))
        if numpy.any(self.centerofmass > allbb[0]) or numpy.any(self.centerofmass < allbb[1]):
            logging.error('the center of mass not locate inside bounding box of the shapes')
            logging.debug('center of mass: %s', str(self.centerofmass))
            logging.debug('bounding box: %s', str(allbb))
            #valid = False
        # calc inertia matrix from bounding box and compare with self.inertia
        bbinertia = self.estimateinertia(allbb)
        if numpy.allclose(self.inertia, bbinertia) == False:
            logging.warn('the inertia matrix is far from the values estimated from bounding box of the shapes')
            logging.debug('inertia calculated from bounding box: %s', bbinertia)
            logging.debug('inertia of the link: %s', self.inertia)
        return valid

    def getbbox(self):
        # calc bounding box from all the shapes
        allbb = [
            [-numpy.Inf, -numpy.Inf, -numpy.Inf],
            [numpy.Inf, numpy.Inf, numpy.Inf]
        ]
        for s in self.visuals + self.collisions:
            bb = s.getbbox()
            #logging.debug('bounding box: %s %s', str(type(s.data)), str(bb))
            allbb[0] = numpy.maximum(allbb[0], bb[0])
            allbb[1] = numpy.minimum(allbb[1], bb[1])
        return allbb

    def estimatemass(self, bbox=None, spgr=1):
        # calc mass from bounding box
        if bbox is None:
            bbox = self.getbbox()
        bblen = [0, 0, 0]
        for i in range(0, 3):
            bblen[i] = bbox[0][i] - bbox[1][i]
        half = (bbox[0] - bbox[1]) / 2
        center = bbox[1] + half
        bbmass = bblen[0] * bblen[1] * bblen[2] * spgr
        return (bbmass, center)
    
    def estimateinertia(self, bbox=None):
        # calc inertia matrix from bounding box
        if bbox is None:
            bbox = self.getbbox()
        bblen = [0, 0, 0]
        for i in range(0, 3):
            bblen[i] = bbox[0][i] - bbox[1][i]
        bbinertia = numpy.diag([
            self.mass * (bblen[1] * bblen[1] + bblen[2] * bblen[2]) / 12,
            self.mass * (bblen[0] * bblen[0] + bblen[2] * bblen[2]) / 12,
            self.mass * (bblen[0] * bblen[0] + bblen[1] * bblen[1]) / 12
        ])
        return bbinertia
    
    def translate(self, mat):
        self.matrix = numpy.dot(self.getmatrix(), mat)
        self.trans = None
        self.rot = None
        for v in self.visuals:
            v.matrix = numpy.dot(v.getmatrix(), mat)
            v.trans = None
            v.rot = None
        for c in self.collisions:
            c.matrix = numpy.dot(c.getmatrix(), mat)
            c.trans = None
            c.rot = None
        if self.centerofmass is not None:
            self.centerofmass[0] += mat[0, 3]
            self.centerofmass[1] += mat[1, 3]
            self.centerofmass[2] += mat[2, 3]
        if self.inertia is not None:
            # same as dMassTranslate function of ODE
            chat = self.crossmat(self.centerofmass)
            ahat = self.crossmat(self.centerofmass + mat[:3, 3])
            t1 = numpy.dot(ahat, ahat)
            t2 = numpy.dot(chat, chat)
            self.inertia += self.mass * (t1 - t2)

    def crossmat(self, c):
        chat = numpy.zeros([3, 3])
        chat[1][2] = c[0]
        chat[2][1] = -c[0]
        chat[2][0] = c[1]
        chat[0][2] = -c[1]
        chat[0][1] = c[2]
        chat[1][0] = -c[2]
        return chat

class JointModel(TransformationModel):
    """
    Joint model
    """
    J_FIXED = 'fixed'            #: Fixed type
    J_REVOLUTE = 'revolute'      #: Revolute type
    J_REVOLUTE2 = 'revolute2'    #: Revolute (2-axis) type
    J_PRISMATIC = 'prismatic'    #: Prismatic type
    J_SCREW = 'screw'            #: Screw type
    J_CONTINUOUS = 'continuous'  #: Continuous type
    J_CRAWLER = 'crawler'        #: Crawler type

    name = None             #: Joint name
    jointId = -1            #: Numeric ID of the joint (used in VRML model)
    jointType = None        #: Joint type
    axis = None             #: Joint axis (relative to parent link)
    axis2 = None            #: Joint axis (used the joint type is revolute2)
    parent = None           #: Name of parent link
    child = None            #: Name of child link
    offsetPosition = False  #: Whether offset joint position or not

    def __init__(self):
        TransformationModel.__init__(self)

    def isvalid(self):
        valid = TransformationModel.isvalid(self)
        if self.name is not None:
            logging.info('validating joint %s' % self.name)
        else:
            logging.error('joint name not set')
            valid = False
        if self.jointId == -1:
            logging.warn('jointId not set')
        if self.axis is not None:
            valid = valid and self.axis.isvalid()
        if self.axis2 is not None:
            valid = valid and self.axis2.isvalid()
        return valid

class AxisData(object):
    """
    Joint axis data
    """
    axis = None             #: Joint axis (relative to parent link)
    damping = None          #: Damping factor
    friction = None         #: Friction factor
    limit = [float("inf"),-float("inf")]
                            #: Joint limits (upper and lower limits in 2-dim array)
    velocitylimit = [float("inf"),-float("inf")]
                            #: Velocity limits (upper and lower limits in 2-dim array)
    effortlimit = [float(100)]

    def isvalid(self):
        valid = True
        if self.limit[0] < self.limit[1]:
            logging.error('upper joint limit is smaller than the lower joint limit')
            valid = False
        if self.limit[0] == self.limit[1]:
            logging.warn('upper and lower joint limit is same (there is no space to move the joint)')
        if self.velocitylimit[0] < self.velocitylimit[1]:
            logging.error('upper velocity limit is smaller than the lower velocity limit')
            valid = False
        if self.velocitylimit[0] < 0:
            logging.error('upper velocity limit is smaller than zero')
            valid = False
        if self.velocitylimit[1] > 0:
            logging.error('lower velocity limit is larger than zero')
            valid = False
        return valid

class ShapeModel(TransformationModel):
    """
    Shape model
    """
    SP_MESH = 'mesh'         #: Mesh shape
    SP_BOX = 'box'           #: Box shape
    SP_CYLINDER = 'cylinder' #: Cylinder shape
    SP_SPHERE = 'sphere'     #: Sphere shape

    name = None              #: Shape name
    shapeType = None         #: Shape type
    data = None              #: Store properties for each specific type of shape

    def __init__(self):
        TransformationModel.__init__(self)

    def isvalid(self):
        valid = TransformationModel.isvalid(self)
        return valid
        
    def getbbox(self):
        bb = self.data.getbbox()
        # generate rectangle mesh from the bounding box
        mesh = MeshData()
        mesh.vertex = numpy.ndarray([8, 3])
        i = 0
        for x in [0, 1]:
            for y in [0, 1]:
                for z in [0, 1]:
                    mesh.vertex[i][0] = bb[x][0]
                    mesh.vertex[i][1] = bb[y][1]
                    mesh.vertex[i][2] = bb[z][2]
                    i = i + 1
        # apply transformation to generated rectangle
        trans = MeshTransformData()
        trans.matrix = self.getmatrix()
        trans.trans = None
        trans.rot = None
        trans.scale = None
        trans.children = [mesh]
        return trans.getbbox()


class MeshTransformData(TransformationModel):
    """
    Mesh transform data

    Intended to store scenegraph structure inside collada or vrml
    """
    children = []      #: Children (store MeshData or MeshTransformData)

    def __init__(self):
        TransformationModel.__init__(self)
        self.children = []

    def maxv(self, trans=None):
        mv = numpy.array([-numpy.Inf, -numpy.Inf, -numpy.Inf, -numpy.Inf])
        if trans is None:
            trans = numpy.identity(4)
        if self.matrix is not None:
            trans2 = numpy.dot(trans, self.getmatrix())
        else:
            trans2 = trans
        for c in self.children:
            if type(c) == MeshTransformData:
                mv = numpy.maximum(mv, c.maxv(trans2))
            elif type(c) == MeshData:
                for v in c.vertex:
                    mv = numpy.maximum(mv, numpy.dot(trans2, numpy.append(v, 1)))
        return numpy.array(mv).reshape(4)

    def minv(self, trans=None):
        mv = numpy.array([numpy.Inf, numpy.Inf, numpy.Inf, numpy.Inf])
        if trans is None:
            trans = numpy.identity(4)
        if self.matrix is not None:
            trans2 = numpy.dot(trans, self.getmatrix())
        else:
            trans2 = trans
        for c in self.children:
            if type(c) == MeshTransformData:
                mv = numpy.minimum(mv, c.minv(trans2))
            elif type(c) == MeshData:
                for v in c.vertex:
                    mv = numpy.minimum(mv, numpy.dot(trans2, numpy.append(v, 1)))
        return numpy.array(mv).reshape(4)

    def getcenter(self):
        maxv = self.maxv()
        minv = self.minv()
        half = (maxv - minv) / 2
        center = minv + half
        return center[0:3]

    def getbbox(self):
        maxv = self.maxv()[0:3]
        minv = self.minv()[0:3]
        return [maxv, minv]

    def pretranslate(self, trans=None):
        '''
        Apply translation to vertex and normals to make translation matrix diagonal
        '''
        if trans is None:
            trans = numpy.identity(4)
        trans2 = numpy.dot(trans, self.getmatrix())
        for c in self.children:
            if type(c) == MeshTransformData:
                c.pretranslate(trans2)
            elif type(c) == MeshData:
                c.vertex = c.vertex.copy()
                for i in range(0, c.vertex.shape[0]):
                    c.vertex[i] = numpy.dot(trans2[:3,:3], c.vertex[i]) + trans2[:3,3]
                if c.normal is not None:
                    c.normal = c.normal.copy()
                    for i in range(0, c.normal.shape[0]):
                        c.normal[i] = numpy.dot(trans2[:3,:3], c.normal[i])
        self.matrix = numpy.identity(4)


class MeshData(object):
    """
    Mesh data
    """
    vertex = []          #: Vertex position ([x,y,z] * N numpy matrix)
    vertex_index = []    #: Vertex index  ([p1,p2,p3] * N numpy matrix)
    normal = None        #: Normal direction ([x,y,z] * N numpy matrix)
    normal_index = None  #: Normal index  ([p1,p2,p3] * N numpy matrix)
    color = None         #: Color ([R,G,B,A] * N numpy matrix)
    color_index = None   #: Color index  ([p1,p2,p3] * N numpy matrix)
    uvmap = None         #: UV mapping ([u,v] * N numpy matrix)
    uvmap_index = None   #: Vertex index  ([p1,p2,p3] * N numpy matrix)
    material = None      #: Name of material

    def __init__(self):
        self.vertex = []
        self.vertex_index = []

    def getbbox(self):
        maxv = numpy.array([-numpy.Inf, -numpy.Inf, -numpy.Inf])
        minv = numpy.array([numpy.Inf, numpy.Inf, numpy.Inf])
        for v in self.vertex:
            maxv = numpy.maximum(maxv, v)
            minv = numpy.minimum(minv, v)
        return [maxv, minv]


class BoxData(object):
    """
    Box shape data
    """
    x = None             #: Width
    y = None             #: Height
    z = None             #: Depth
    material = None      #: Name of material

    def getbbox(self):
        return [
            [self.x/2, self.y/2, self.z/2],
            [-self.x/2, -self.y/2, -self.z/2]
        ]


class CylinderData(object):
    """
    Cylinder shape data
    """
    radius = None        #: Radius
    height = None        #: Height
    material = None      #: Name of material

    def getbbox(self):
        return [
            [self.radius, self.height/2, self.radius],
            [-self.radius, -self.height/2, -self.radius]
        ]


class SphereData(object):
    """
    Sphere shape data
    """
    radius = None        #: Radius
    material = None      #: Name of material

    def getbbox(self):
        return [
            [self.radius, self.radius, self.radius],
            [-self.radius, -self.radius, -self.radius]
        ]


class SensorModel(TransformationModel):
    """
    Sensor model
    """
    SS_CAMERA = "camera"  #: Camera (color, mono, depth)
    SS_RAY = "ray"        #: Laser range finder
    SS_IMU = "imu"        #: IMU sensor

    name = None           #: Name
    sensorType = None     #: Type of sensor
    parent = None         #: Name of parent link
    rate = 20             #: Update rate of sensor
    data = None

    def __init__(self):
        TransformationModel.__init__(self)


class CameraData(object):
    """
    Camera sensor data
    """
    CS_COLOR = "color"
    CS_MONO = "mono"
    CS_DEPTH = "depth"
    CS_RGBD = "rgbd"

    cameraType = None    #: Camera type
    near = 0.01          #: Near clip distance
    far = 50.0           #: Far clip distance
    fov = 1.5708         #: Field of view (horizontal)
    width = 640          #: Width
    height = 480         #: Height


class RayData(object):
    """
    Ray sensor data
    """
    min_angle = 0
    max_angle = 0
    min_range = 0
    max_range = 0


class MaterialModel(object):
    """
    Material model
    """
    name = None          #: Name of the material
    ambient = None       #: [r,g,b,a] array
    diffuse = None       #: [r,g,b,a] array
    specular = None      #: [r,g,b,a] array
    emission = None      #: [r,g,b,a] array
    shininess = None     #: float value or path string of texture image
    transparency = None  #: float value or path string of texture image
    texture = None       #: path string of texture image

    def __init__(self):
        self.diffuse = [0.8, 0.8, 0.8, 1.0]
