# -*- coding:utf-8 -*-

"""
Reader and writer for URDF format
"""

import lxml
import numpy
import jinja2
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
            with l.find('inertial') as inertial:
                lm.inertia = self.readInertia(inertial.find('inertia'))
                lm.trans = self.readOrigin(inertial.find('origin'))
                lm.mass = self.readMass(inertial.find('mass'))
            with l.find('visual') as visual:
                sm = model.ShapeModel
                sm.trans = self.readOrigin(visual.find('origin'))
                with visual.find('geometry') as geometry:
                    with geometry.find('mesh') as mesh:
                        sm.shapeType = m.SP_MESH
                        reader = collada.ColladaReader
                        sm.mesh = reader.read(self.resolveFile(mesh.attrib['filename']))
                lm.visual = sm
            with l.find('collision') as collision:
                sm = model.ShapeModel
                sm.trans = self.readOrigin(collision.find('origin'))
                with collision.find('geometry') as geometry:
                    with geometry.find('mesh') as mesh:
                        sm.shapeType = m.SP_MESH
                        reader = stl.STLReader
                        sm.mesh = reader.read(self.resolveFile(mesh.attrib['filename']))
                lm.collision = sm
            bm.links.append(lm)

        for j in d.findAll('joint'):
            jm = model.JointModel
            jm.origin = self.readOrigin(j.find('origin'))
            jm.axis = j.find('axis').attrib['xyz']
            jm.parent = j.find('parent').attrib['link']
            jm.child = j.find('child').attrib['link']
            with j.find('dynamics') as dynamics:
                jm.damping = dynamics.attrib['damping']
                jm.friction = dynamics.attrib['friction']
            with j.find('limit') as limit:
                jm.limit = [limit.attrib['upper'], limit.attrib['lower']]
            bm.joints.append(jm)

        return bm

    def readOrigin(self, d):
        xyz = numpy.matrix(d.attrib['xyz'])
        rpy = numpy.matrix(d.attrib['rpy'])

    def readInertia(self, d):
        inertia = numpy.zeros((3,3))
        inertia[0,0] = float(d.attrib['ixx'])
        inertia[0,1] = inertia[1,0] = float(d.attrib['ixy'])
        inertia[0,2] = inertia[2,0] = float(d.attrib['ixz'])
        inertia[1,1] = float(d.attrib['iyy'])
        inertia[1,2] = inertia[2,1] = float(d.attrib['iyz'])
        inertia[2,2] = float(d.attrib['izz'])

    def readMass(self, d):
        return float(d.attrib['value'])

    def resolveFile(self, f):
        if f.count('package://') > 0:
            pkgname = f.lstrip('package://').split('/')[0]
            ppath = subprocess.check_output(['rospack', 'find', pkgname]).rstrip()
            return os.path.join(ppath, f.lstrip('package://'))
        return f


class URDFWriter:
    def write(self, m, f):
        pass
