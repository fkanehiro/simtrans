# -*- coding:utf-8 -*-

"""
Common data structure for model converter
"""

import numpy


class ProjectModel(object):
    """
    Project model
    """
    name = None        #: Name of the simulation
    bodies = []        #: List of body models

    def __init__(self):
        self.bodies = []


class BodyModel(object):
    """
    Body model
    """
    name = None        #: Name of the body
    links = []         #: List of links
    joints = []        #: List of joints
    scale = None       #: XYZ scale vector
    trans = None       #: XYZ translation vector
    rot = None         #: Rotation (quaternion representation)

    def __init__(self):
        self.links = []
        self.joints = []


class LinkModel(object):
    """
    Link model
    """
    name = None        #: Name of the link
    mass = 0           #: Mass of the link
    inertia = None     #: Inertia (vector representation of 3x3 matrix)
    visual = None      #: Shape information used for rendering
    collision = None   #: Shape information used for collision detection
    sensors = None     #: List of sensors
    scale = None       #: XYZ scale vector
    trans = None       #: XYZ translation vector
    rot = None         #: Rotation (quaternion representation)

    def __init__(self):
        self.trans = [0, 0, 0]
        self.inertia = numpy.identity(3)


class JointModel(object):
    """
    Joint model
    """
    J_FIXED = 'fixed'         #: Fixed type
    J_REVOLUTE = 'revolute'   #: Revolute type
    J_PRISMATIC = 'prismatic' #: Prismatic type
    J_SCREW = 'screw'         #: Screw type

    jointType = None   #: Joint type
    axis = None        #: Joint axis
    parent = None      #: Parent link
    child = None       #: Child link
    damping = None     #: Damping
    friction = None    #: Friction
    limit = None       #: Joint limits (upper and lower in vector)
    trans = None       #: XYZ translation vector
    rot = None         #: Rotation (quaternion representation)


class NodeModel(object):
    children = []      #: Shape data
    scale = None       #: XYZ scale vector
    trans = None       #: XYZ translation vector
    rot = None         #: Rotation (quaternion representation)

    def __init__(self):
        self.children = []


class ShapeModel(object):
    """
    Shape model
    """
    SP_MESH = 'mesh'         #: Mesh shape
    SP_BOX = 'box'           #: Box shape
    SP_CYLINDER = 'cylinder' #: Cylinder shape
    SP_SPHERE = 'sphere'     #: Sphere shape

    shapeType = None   #: Shape type
    data = None        #: Shape data
    image = None


class MeshData(object):
    vertex = []       #: Vertex position (in x,y,z * 3 * N format)
    vertex_index = []
    normal = None     #: Normal direction
    normal_index = None
    color = None      #: Color (in RGBA * N format)
    color_index = None
    uvmap = None      #: UV mapping (in x,y * N format)
    uvmap_index = None

    def __init__(self):
        self.vertex = []
        self.vertex_index = []


class BoxData(object):
    x = None
    y = None
    z = None


class CylinderData(object):
    radius = None
    height = None


class SphereData(object):
    radius = None


class SensorModel(object):
    """
    Sensor model
    """
    sensorType = None  #: Type of sensor
    trans = None       #: XYZ translation vector
    rot = None         #: Rotation (quaternion representation)
