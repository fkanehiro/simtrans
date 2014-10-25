# -*- coding:utf-8 -*-

"""
Reader and writer for SDF format
"""

import os
import lxml
import lxml.etree
import numpy
try:
    from .thridparty import transformations as tf
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
        >>> m = r.read('~/gazebo_models/pr2/model.sdf')
        '''
        bm = model.BodyModel()
        d = lxml.etree.parse(open(fname))

        for l in d.findall('link'):
            # general information
            lm = model.LinkModel()
            lm.name = l.attrib['name']
            # phisical property
            inertial = l.find('inertial')
            if inertial is not None:
                lm.inertia = self.readInertia(inertial.find('inertia'))
                lm.trans, lm.rot = self.readPose(inertial.find('pose'))
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

        for j in d.findall('joint'):
            jm = model.JointModel()
            # general property
            jm.name = j.attrib['name']
            jm.jointType = self.readJointType(j.attrib['type'])
            jm.trans, jm.rot = self.readOrigin(j.find('origin'))
            axis = j.find('axis')
            if axis is not None:
                jm.axis = axis.attrib['xyz']
            jm.parent = j.find('parent').attrib['link']
            jm.child = j.find('child').attrib['link']
            # phisical property
            dynamics = j.find('dynamics')
            if dynamics is not None:
                jm.damping = dynamics.attrib['damping']
                jm.friction = dynamics.attrib['friction']
            limit = j.find('limit')
            if limit is not None:
                jm.limit = [limit.attrib['upper'], limit.attrib['lower']]
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
        raise Exception('unsupported joint type')

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
        sm.trans, sm.rot = self.readPose(d.find('pose'))
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
                print "unsupported shape type: %s" % g.tag
        return sm

    def resolveFile(self, f):
        '''
        Resolve file by replacing ROS file path heading "model://"

        >>> r = SDFReader()
        >>> r.resolveFile('model://pr2/model.sdf')
        '/opt/ros/indigo/share/pr2/model.sdf'
        >>> r.resolveFile('model://pr2/meshes/base_v0/base.dae')
        '/opt/ros/indigo/share/pr2/meshes/base_v0/base.dae'
        '''
        try:
            if f.count('model://') > 0:
                return f.replace('model://', os.environ['GAZEBO_MODELS'])
        except Exception, e:
            print str(e)
        return f


class SDFWriter(object):
    def write(self, m, f):
        pass
