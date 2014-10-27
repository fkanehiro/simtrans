# -*- coding:utf-8 -*-

"""
Reader and writer for SDF format
"""

from logging import getLogger
logger = getLogger(__name__)

import os
import lxml.etree
import numpy
try:
    from .thirdparty import transformations as tf
except UserWarning:
    pass
import jinja2
from . import model
from . import collada
from . import stl


class SDFReader(object):
    '''
    SDF reader class
    '''
    def read(self, fname):
        '''
        Read SDF model data given the model file

        >>> r = SDFReader()
        >>> m = r.read('model://pr2/model.sdf')
        '''
        bm = model.BodyModel()
        d = lxml.etree.parse(open(self.resolveFile(fname)))
        dm = d.find('model')
        bm.name = dm.attrib['name']

        for l in dm.findall('link'):
            # general information
            lm = model.LinkModel()
            lm.name = l.attrib['name']
            # phisical property
            inertial = l.find('inertial')
            if inertial is not None:
                lm.inertia = self.readInertia(inertial.find('inertia'))
                pose = inertial.find('pose')
                if pose is not None:
                    lm.trans, lm.rot = self.readPose(pose)
                lm.mass = self.readMass(inertial.find('mass'))
            # visual property
            visual = l.find('visual')
            if visual is not None:
                lm.visual = self.readShape(visual)
            # contact property
            collision = l.find('collision')
            if collision is not None:
                lm.collision = self.readShape(collision)
            bm.links.append(lm)

        for j in dm.findall('joint'):
            jm = model.JointModel()
            # general property
            jm.name = j.attrib['name']
            jm.jointType = self.readJointType(j.attrib['type'])
            pose = j.find('pose')
            if pose is not None:
                jm.trans, jm.rot = self.readPose(pose)
            axis = j.find('axis')
            if axis is not None:
                jm.axis = axis.find('xyz').text
                dynamics = axis.find('dynamics')
                if dynamics is not None:
                    jm.damping = dynamics.find('damping').text
                    jm.friction = dynamics.find('friction').text
                limit = axis.find('limit')
                if limit is not None:
                    jm.limit = [limit.find('upper').text, limit.find('lower').text]
            jm.parent = j.find('parent').text
            jm.child = j.find('child').text
            # phisical property
            bm.joints.append(jm)

        return bm

    def readPose(self, doc):
        pose = None
        xyz = None
        trans = None
        try:
            pose = [float(v) for v in doc.text.split(' ')]
            xyz = [pose[0], pose[1], pose[2]]
            trans = tf.quaternion_from_euler(pose[3], pose[4], pose[5])
        except KeyError:
            pass
        return xyz, trans

    def readJointType(self, d):
        if d == "fixed":
            return model.JointModel.J_FIXED
        elif d == "revolute":
            return model.JointModel.J_REVOLUTE
        elif d == 'prismatic':
            return model.JointModel.J_PRISMATIC
        elif d == 'screw':
            return model.JointModel.J_SCREW
        raise Exception('unsupported joint type: %s' % d)

    def readInertia(self, d):
        inertia = numpy.zeros((3, 3))
        inertia[0, 0] = float(d.find('ixx').text)
        inertia[0, 1] = inertia[1, 0] = float(d.find('ixy').text)
        inertia[0, 2] = inertia[2, 0] = float(d.find('ixz').text)
        inertia[1, 1] = float(d.find('iyy').text)
        inertia[1, 2] = inertia[2, 1] = float(d.find('iyz').text)
        inertia[2, 2] = float(d.find('izz').text)
        return inertia

    def readMass(self, d):
        return float(d.text)

    def readShape(self, d):
        sm = model.ShapeModel()
        pose = d.find('pose')
        if pose is not None:
            sm.trans, sm.rot = self.readPose(pose)
        for g in d.find('geometry').getchildren():
            if g.tag == 'mesh':
                # print "reading mesh " + mesh.attrib['filename']
                filename = self.resolveFile(g.find('uri').text)
                fileext = os.path.splitext(filename)[1]
                sm.shapeType = model.ShapeModel.SP_NONE
                if fileext == '.dae':
                    reader = collada.ColladaReader()
                else:
                    reader = stl.STLReader()
                sm.children.append(reader.read(filename))
            elif g.tag == 'box':
                sm.shapeType = model.ShapeModel.SP_BOX
                size = [float(v) for v in g.find('size').text.split(' ')]
            elif g.tag == 'cylinder':
                sm.shapeType = model.ShapeModel.SP_CYLINDER
                radius = float(g.find('radius').text)
                length = float(g.find('length').text)
            else:
                raise Exception('unsupported shape type: %s' % g.tag)
        return sm

    def resolveFile(self, f):
        '''
        Resolve file by replacing ROS file path heading "model://"
        '''
        try:
            if f.count('model://') > 0:
                return os.path.join(os.environ['GAZEBO_MODELS'], f.replace('model://', ''))
        except Exception, e:
            logger.warn(str(e))
        return f


class SDFWriter(object):
    def write(self, m, f):
        pass
