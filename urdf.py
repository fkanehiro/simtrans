# -*- coding:utf-8 -*-

"""
Reader and writer for URDF format
"""

import lxml
import numpy
import model
import collada
import stl


class URDFReader:
    def read(self, f):
        bm = model.BodyModel
        d = lxml.etree.parse(open(f))

        for l in d.findAll('link'):
            lm = model.LinkModel
            lm.name = l.attrib['name']
            inertial = l.find('inertial')
            lm.inertia = self.readInertia(inertial.find('inertial'))
            lm.trans = self.readOrigin(inertial.find('origin'))
            lm.mass = self.readMass(inertial.find('mass'))
            lm.visual = self.readVisual(l.find('visual'))
            lm.collision = self.readCollision(l.find('collision'))

        for j in d.findAll('joint'):
            jm = model.JointModel
            jm.origin = self.readOrigin(j.find('origin'))

    def readOrigin(self, d):
        xyz = d.attrib['xyz'].split(' ')
        rpy = d.attrib['rpy'].split(' ')

    def readInertia(self, d):
        inertia = numpy.matrix
        inertia = d.attrib['ixx']

    def readMass(self, d):
        return float(d.attrib['value'])

    def readVisual(self, d):
        m = model.ShapeModel
        m.shapeType = m.SP_MESH
        reader = collada.ColladaReader
        m.mesh = reader.read(d.find('geometry').find('mesh').attrib['filename'])

class URDFWriter:
    def write(self, m, f):
        pass
