# -*- coding:utf-8 -*-

"""
Reader and writer for URDF format
"""

import os
import subprocess
import lxml.etree
import numpy
import euclid
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
        >>> r.read('/opt/ros/indigo/share/atlas_description/urdf/atlas_v3.urdf')
        <class 'simtrans.model.BodyModel'>
        '''
        bm = model.BodyModel
        d = lxml.etree.parse(open(fname))

        for l in d.findall('link'):
            # general information
            lm = model.LinkModel
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
            jm = model.JointModel
            # general property
            jm.name = j.attrib['name']
            jm.jointType = j.attrib['type']
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
        try:
            xyz = numpy.matrix(doc.attrib['xyz'])
            rpy = numpy.matrix(doc.attrib['rpy'])
        except KeyError:
            pass
        return xyz, rpy

    def readInertia(self, d):
        inertia = numpy.zeros((3, 3))
        inertia[0, 0] = float(d.attrib['ixx'])
        inertia[0, 1] = inertia[1, 0] = float(d.attrib['ixy'])
        inertia[0, 2] = inertia[2, 0] = float(d.attrib['ixz'])
        inertia[1, 1] = float(d.attrib['iyy'])
        inertia[1, 2] = inertia[2, 1] = float(d.attrib['iyz'])
        inertia[2, 2] = float(d.attrib['izz'])

    def readMass(self, d):
        return float(d.attrib['value'])

    def readShape(self, d):
        sm = model.ShapeModel
        sm.trans, sm.rot = self.readOrigin(d.find('origin'))
        mesh = d.find('geometry/mesh')
        if mesh is not None:
            filename = self.resolveFile(mesh.attrib['filename'])
            fileext = os.path.splitext(filename)[1]
            sm.shapeType = model.ShapeModel.SP_MESH
            if fileext == '.dae':
                reader = collada.ColladaReader()
            else:
                reader = stl.STLReader()
                sm.mesh = reader.read(filename)
        return sm

    def resolveFile(self, f):
        '''
        Resolve file by repacing ROS file path heading "package://"

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
        except Exception, err:
            print str(err)
        return f


class URDFWriter(object):
    '''
    URDF writer class
    '''
    def write(self, m, f):
        pass
