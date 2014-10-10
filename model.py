# -*- coding:utf-8 -*-

"""
Common data structure for model converter
"""


class ProjectModel(object):
    name = None
    body = None


class BodyModel(object):
    name = None


class LinkModel(object):
    """Link model

    Attributes:
       inertial
       visual
    """
    inertial = None
    visual = None
    collision = None
    trans = None
    rot = None


class JointModel(object):
    """
    Joint model
    """
    jointType = None
    parent = None
    child = None
    damping = None
    friction = None
    limit = None
    trans = None
    rot = None


class ShapeModel(object):
    """
    Shape model
    """
    TYPE_MESH = 1
    shapeType = None


class MeshModel(object):
    vertex = None
    normal = None
    color = None
    uvmap = None
    image = None


class SensorModel(object):
    sensorType = None
    trans = None
    rot = None
