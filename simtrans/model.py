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
    J_FIXED = 1        #: Fixed type
    J_REVOLUTE = 2     #: Revolute type
    J_PRISMATIC = 3    #: Prismatic type
    J_SCREW = 4        #: Screw type

    jointType = None   #: Joint type
    axis = None        #: Joint axis
    parent = None      #: Parent link
    child = None       #: Child link
    damping = None     #: Damping
    friction = None    #: Friction
    limit = None       #: Joint limits (upper and lower in vector)
    trans = None       #: XYZ translation vector
    rot = None         #: Rotation (quaternion representation)


class ShapeModel(object):
    """
    Shape model
    """
    SP_NONE = 0        #: None shape (only transform)
    SP_MESH = 1        #: Mesh shape
    SP_BOX = 2         #: Box shape
    SP_CYLINDER = 3    #: Cylinder shape
    SP_CONE = 4        #: Cone shape
    SP_SPHERE = 5      #: Sphere shape
    SP_PLANE = 6       #: Plane shape

    shapeType = None   #: Shape type
    children = []      #: Mesh data (if the type is SP_MESH)
    image = None
    scale = None       #: XYZ scale vector
    trans = None       #: XYZ translation vector
    rot = None         #: Rotation (quaternion representation)

    def __init__(self):
        self.children = []


class MeshModel(object):
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


class SensorModel(object):
    """
    Sensor model
    """
    sensorType = None  #: Type of sensor
    trans = None       #: XYZ translation vector
    rot = None         #: Rotation (quaternion representation)
