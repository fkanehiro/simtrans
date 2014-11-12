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

    def __init__(self):
        self.matrix = numpy.identity(4)

    def gettranslation(self):
        translation, scale, axis = hrputil.decomposeMatrix(self.matrix)
        return translation

    def applytranslation(self, v):
        self.matrix = self.matrix * tf.translation_matrix(v)

    def getscale(self):
        transform, scale, axis = hrputil.decomposeMatrix(self.matrix)
        return scale

    def applyscale(self, v):
        self.matrix = self.matrix * tf.scale_matrix(v)

    def getrpy(self):
        m = self.matrix.copy()
        return tf.euler_from_matrix(m)

    def applyrpy(self, v):
        self.matrix = self.matrix * tf.euler_matrix(v[0], v[1], v[2])

    def getangle(self):
        transform, scale, axis = hrputil.decomposeMatrix(self.matrix)
        return axis

    def applyangle(self, v):
        v2 = v[0] * v[1]
        self.matrix = self.matrix * tf.rotation_matrix(v2[0], v2[1], v2[2])


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
    J_FIXED = 'fixed'          #: Fixed type
    J_REVOLUTE = 'revolute'    #: Revolute type
    J_PRISMATIC = 'prismatic'  #: Prismatic type
    J_SCREW = 'screw'          #: Screw type

    name = None        #: Joint name
    jointType = None   #: Joint type
    axis = None        #: Joint axis (relative to parent link)
    parent = None      #: Name of parent link
    child = None       #: Name of child link
    damping = None     #: Damping factor
    friction = None    #: Friction factor
    limit = None       #: Joint limits (upper and lower limits in 2-dim array)

    def __init__(self):
        TransformationModel.__init__(self)
        self.limit = [1, 1]


class ShapeModel(TransformationModel):
    """
    Shape model
    """
    SP_MESH = 'mesh'         #: Mesh shape
    SP_BOX = 'box'           #: Box shape
    SP_CYLINDER = 'cylinder' #: Cylinder shape
    SP_SPHERE = 'sphere'     #: Sphere shape

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
    SS_RANGE = "range"    #: Laser range finder
    SS_IMU = "imu"        #: IMU sensor

    sensorType = None  #: Type of sensor
    parent = None      #: Name of parent link
    data = None

    def __init__(self):
        TransformationModel.__init__(self)


class MaterialModel(object):
    """
    Material model
    """
    name = None          #: Name of the material
    ambient = None       #: [r,g,b,a] array or path string of texture image
    diffuse = None       #: [r,g,b,a] array or path string of texture image
    specular = None      #: [r,g,b,a] array or path string of texture image
    emission = None      #: [r,g,b,a] array or path string of texture image
    shininess = None     #: float value or path string of texture image
    transparency = None  #: float value or path string of texture image
