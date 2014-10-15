# -*- coding:utf-8 -*-

"""
Common data structure for model converter
"""


class ProjectModel(object):
    """
    Project model
    """
    name = None        #: Name of the simulation
    bodies = []        #: List of body models


class BodyModel(object):
    """
    Body model
    """
    name = None        #: Name of the body
    links = []         #: List of links
    joints = []        #: List of joints
    trans = None       #: XYZ translation vector
    rot = None         #: Rotation (quaternion representation)


class LinkModel(object):
    """
    Link model
    """
    name = None        #: Name of the link
    mass = 0           #: Mass of the link
    inertial = None    #: Inertial (vector representation of 3x3 matrix)
    visual = None      #: Shape information used for rendering
    collision = None   #: Shape information used for collision detection
    sensors = None     #: List of sensors
    trans = None       #: XYZ translation vector
    rot = None         #: Rotation (quaternion representation)


class JointModel(object):
    """
    Joint model
    """
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
    SP_MESH = 1        #: Mesh shape
    SP_BOX = 2         #: Box shape
    SP_CYLINDER = 3    #: Cylinder shape
    SP_CONE = 4        #: Cone shape
    SP_SPHERE = 5      #: Sphere shape
    SP_PLANE = 6       #: Plane shape

    shapeType = None   #: Shape type
    mesh = None        #: Mesh data (if the type is SP_MESH)
    trans = None       #: XYZ translation vector
    rot = None         #: Rotation (quaternion representation)


class MeshModel(object):
    """
    Mesh model
    """
    vertex = []       #: Vertex position (in x,y,z * 3 * N format)
    normal = []       #: Normal direction
    color = []        #: Color (in RGBA * N format)
    uvmap = []        #: UV mapping (in x,y * N format)
    image = None      #: Texture image
    trans = None      #: XYZ translation vector
    rot = None        #: Rotation (quaternion representation)


class SensorModel(object):
    """
    Sensor model
    """
    sensorType = None  #: Type of sensor
    trans = None       #: XYZ translation vector
    rot = None         #: Rotation (quaternion representation)
