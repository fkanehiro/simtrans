# -*- coding:utf-8 -*-

"""
Reader and writer for URDF format
"""

import os
import subprocess
import lxml.etree
import numpy
from .thridparty import transformations as tf
import jinja2
from . import model
from . import collada
from . import stl


class URDFReader(object):
    '''
    URDF reader class
    '''
    def read(self, fname):
        '''
        Read URDF model data given the model file

        >>> r = URDFReader()
        >>> m = r.read('/opt/ros/indigo/share/atlas_description/urdf/atlas_v3.urdf')
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
                lm.trans, lm.rot = self.readOrigin(inertial.find('origin'))
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

    def readOrigin(self, doc):
        xyz = None
        rpy = None
        trans = None
        try:
            xyz = [float(v) for v in doc.attrib['xyz'].split(' ')]
            rpy = [float(v) for v in doc.attrib['rpy'].split(' ')]
            trans = tf.quaternion_from_euler(rpy[0], rpy[1], rpy[2])
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
        inertia[0, 0] = float(d.attrib['ixx'])
        inertia[0, 1] = inertia[1, 0] = float(d.attrib['ixy'])
        inertia[0, 2] = inertia[2, 0] = float(d.attrib['ixz'])
        inertia[1, 1] = float(d.attrib['iyy'])
        inertia[1, 2] = inertia[2, 1] = float(d.attrib['iyz'])
        inertia[2, 2] = float(d.attrib['izz'])
        return inertia

    def readMass(self, d):
        return float(d.attrib['value'])

    def readShape(self, d):
        sm = model.ShapeModel()
        sm.trans, sm.rot = self.readOrigin(d.find('origin'))
        mesh = d.find('geometry').find('mesh')
        if mesh is not None:
            # print "reading mesh " + mesh.attrib['filename']
            filename = self.resolveFile(mesh.attrib['filename'])
            fileext = os.path.splitext(filename)[1]
            sm.shapeType = model.ShapeModel.SP_NONE
            if fileext == '.dae':
                reader = collada.ColladaReader()
            else:
                reader = stl.STLReader()
            sm.children.append(reader.read(filename))
        return sm

    def resolveFile(self, f):
        '''
        Resolve file by replacing ROS file path heading "package://"

        >>> r = URDFReader()
        >>> r.resolveFile('package://atlas_description/package.xml')
        '/opt/ros/indigo/share/atlas_description/package.xml'
        >>> r.resolveFile('package://atlas_description/urdf/atlas.urdf')
        '/opt/ros/indigo/share/atlas_description/urdf/atlas.urdf'
        '''
        try:
            if f.count('package://') > 0:
                pkgname, pkgfile = f.replace('package://', '').split('/', 1)
                ppath = subprocess.check_output(['rospack', 'find', pkgname]).rstrip()
                return os.path.join(ppath, pkgfile)
        except Exception, e:
            print str(e)
        return f


class URDFWriter(object):
    '''
    URDF writer class
    '''
    def write(self, m, f):
        pass
