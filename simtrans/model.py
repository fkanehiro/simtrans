# -*- coding:utf-8 -*-
# pylint: disable=too-few-public-methods, line-too-long

"""
Common data structure for model converter
"""

from __future__ import absolute_import
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
    >>> numpy.allclose(m.getangle(), [0, 0, 0])
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
            return tf.quaternion_from_matrix(self.matrix)
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


class JointModel(TransformationModel):
    """
    Joint model
    """
    J_FIXED = 'fixed'            #: Fixed type
    J_REVOLUTE = 'revolute'      #: Revolute type
    J_PRISMATIC = 'prismatic'    #: Prismatic type
    J_SCREW = 'screw'            #: Screw type
    J_CONTINUOUS = 'continuous'  #: Continuous type

    name = None             #: Joint name
    jointType = None        #: Joint type
    axis = None             #: Joint axis (relative to parent link)
    parent = None           #: Name of parent link
    child = None            #: Name of child link
    damping = None          #: Damping factor
    friction = None         #: Friction factor
    limit = None            #: Joint limits (upper and lower limits in 2-dim array)
    velocitylimit = None    #: Velocity limits (upper and lower limits in 2-dim array)
    offsetPosition = False  #: Whether offset joint position or not

    def __init__(self):
        TransformationModel.__init__(self)


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
        mv = numpy.array([0, 0, 0, 0])
        if trans is None:
            trans = numpy.identity(4)
        if self.matrix is not None:
            trans2 = numpy.dot(self.matrix, trans)
        else:
            trans2 = trans
        for c in self.children:
            if type(c) == MeshTransformData:
                mv = numpy.maximum(mv, c.maxv(trans2))
            elif type(c) == MeshData:
                for v in c.vertex:
                    mv = numpy.maximum(mv, numpy.dot(trans2, numpy.append(v, 1)))
        return mv

    def minv(self, trans=None):
        mv = numpy.array([numpy.Inf, numpy.Inf, numpy.Inf, numpy.Inf])
        if trans is None:
            trans = numpy.identity(4)
        if self.matrix is not None:
            trans2 = numpy.dot(self.matrix, trans)
        else:
            trans2 = trans
        for c in self.children:
            if type(c) == MeshTransformData:
                mv = numpy.minimum(mv, c.minv(trans2))
            elif type(c) == MeshData:
                for v in c.vertex:
                    mv = numpy.minimum(mv, numpy.dot(trans2, numpy.append(v, 1)))
        return mv

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

class BoxData(object):
    """
    Box shape data
    """
    x = None             #: Width
    y = None             #: Height
    z = None             #: Depth
    material = None      #: Name of material


class CylinderData(object):
    """
    Cylinder shape data
    """
    radius = None        #: Radius
    height = None        #: Height
    material = None      #: Name of material


class SphereData(object):
    """
    Sphere shape data
    """
    radius = None        #: Radius
    material = None      #: Name of material


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
        self.ambient = [0.8, 0.8, 0.8, 1.0]
        self.diffuse = [0.8, 0.8, 0.8, 1.0]
        self.specular = [0.8, 0.8, 0.8, 1.0]
        self.emission = [0.8, 0.8, 0.8, 1.0]
