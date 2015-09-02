# -*- coding:utf-8 -*-

"""Reader and writer for URDF format

:Organization:
 AIST

Requirements
------------
* numpy
* lxml xml parser
* jinja2 template engine

Examples
--------

Read URDF model data given the model file

>>> r = URDFReader()
>>> m = r.read('package://atlas_description/urdf/atlas_v3.urdf')

Write simulation model in URDF format

>>> from . import vrml
>>> r = vrml.VRMLReader()
>>> m = r.read('/home/yosuke/HRP-4C/HRP4Cmain.wrl')
>>> w = URDFWriter()
>>> w.write(m, '/tmp/hrp4c.urdf')
>>> import subprocess
>>> subprocess.check_call('check_urdf /tmp/hrp4c.urdf'.split(' '))
0
"""

import os
import lxml.etree
import numpy
import re
import copy
import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from .thirdparty import transformations as tf
import jinja2
import uuid
import subprocess
import logging
from . import model
from . import collada
from . import stl
from . import utils
from . import sdf


class URDFReader(object):
    '''
    URDF reader class
    '''
    def __init__(self):
        self._assethandler = None

    def read(self, fname, assethandler=None, options=None):
        '''
        Read simulation model in urdf format
        (internally convert to sdf using gz sdf utility)
        '''
        reader = sdf.SDFReader()
        m = reader.read(fname, assethandler)
        return m

    def read2(self, fname, assethandler=None, options=None):
        """Read URDF model data given the model file

        :param fname: path of the file to read
        :param assethandler: asset handler (optional)
        :returns: model data
        :rtype: model.Model

        """
        if assethandler is not None:
            self._assethandler = assethandler

        bm = model.BodyModel()
        d = lxml.etree.parse(open(utils.resolveFile(fname)))

        for j in d.findall('joint'):
            jm = model.JointModel()
            # general property
            jm.name = j.attrib['name']
            jm.jointType = self.readJointType(j.attrib['type'])
            origin = j.find('origin')
            if origin is not None:
                self.readOrigin(jm, origin)
            axis = j.find('axis')
            if axis is not None:
                jm.axis = [float(v) for v in re.split(' +', axis.attrib['xyz'].strip(' '))]
            jm.parent = j.find('parent').attrib['link']
            jm.child = j.find('child').attrib['link']
            # phisical property
            dynamics = j.find('dynamics')
            if dynamics is not None:
                try:
                    jm.damping = float(dynamics.attrib['damping'])
                    jm.friction = float(dynamics.attrib['friction'])
                except KeyError:
                    pass
            limit = j.find('limit')
            if limit is not None:
                try:
                    jm.limit = [float(limit.attrib['upper']), float(limit.attrib['lower'])]
                    velocity = float(limit.attrib['velocity'])
                    jm.velocitylimit = [velocity, -velocity]
                except KeyError:
                    pass
            bm.joints.append(jm)

        for l in d.findall('link'):
            # general information
            lm = model.LinkModel()
            lm.name = l.attrib['name']
            # phisical property
            inertial = l.find('inertial')
            if inertial is not None:
                lm.mass = float(inertial.find('mass').attrib['value'])
                lm.centerofmass = [float(v) for v in re.split(' +', inertial.find('origin').attrib['xyz'].strip(' '))]
                lm.inertia = self.readInertia(inertial.find('inertia'))
            # visual property
            lm.visuals = []
            for v in l.findall('visual'):
                lm.visuals.append(self.readShape(v))
            # contact property
            lm.collisions = []
            for c in l.findall('collision'):
                lm.collisions.append(self.readShape(c))
            bm.links.append(lm)

        self._linkmap = {}
        for l in bm.links:
            self._linkmap[l.name] = l

        for r in utils.findroot(bm):
            self._abslinks = {}
            for c in utils.findchildren(bm, r):
                logging.info("constructing tree from root joint: %s - > %s" % (c.parent, c.child))
                self._abslinks[c.parent] = self._linkmap[c.parent]
                self.convertChild(bm, c)
            bm.links.extend(self._abslinks.values())
        
        return bm

    def convertChild(self, bm, l):
        parent = self._abslinks[l.parent]
        child = self._linkmap[l.child]
        abschild = copy.deepcopy(child)
        abschild.matrix = numpy.dot(parent.getmatrix(), child.getmatrix())
        abschild.trans = None
        abschild.rot = None
        self._abslinks[l.child] = abschild
        l.matrix = abschild.getmatrix()
        l.trans = None
        l.rot = None
        for c in utils.findchildren(bm, l.child):
            self.convertChild(bm, c)
    
    def readOrigin(self, m, doc):
        try:
            m.trans = numpy.array([float(v) for v in re.split(' +', doc.attrib['xyz'].strip(' '))])
        except KeyError:
            pass
        try:
            rpy = [float(v) for v in re.split(' +', doc.attrib['rpy'].strip(' '))]
            m.rot = tf.quaternion_from_euler(rpy[0], rpy[1], rpy[2])
        except KeyError:
            pass

    def readJointType(self, d):
        if d == "fixed":
            return model.JointModel.J_FIXED
        elif d == "revolute":
            return model.JointModel.J_REVOLUTE
        elif d == "revolute2":
            return model.JointModel.J_REVOLUTE2
        elif d == 'prismatic':
            return model.JointModel.J_PRISMATIC
        elif d == 'screw':
            return model.JointModel.J_SCREW
        elif d == 'continuous':
            return model.JointModel.J_CONTINUOUS
        raise Exception('unsupported joint type %s' % d)

    def readInertia(self, d):
        inertia = numpy.zeros((3, 3))
        inertia[0, 0] = float(d.attrib['ixx'])
        inertia[0, 1] = inertia[1, 0] = float(d.attrib['ixy'])
        inertia[0, 2] = inertia[2, 0] = float(d.attrib['ixz'])
        inertia[1, 1] = float(d.attrib['iyy'])
        inertia[1, 2] = inertia[2, 1] = float(d.attrib['iyz'])
        inertia[2, 2] = float(d.attrib['izz'])
        return inertia

    def readShape(self, d):
        sm = model.ShapeModel()
        sm.name = 'shape-' + str(uuid.uuid1()).replace('-', '')
        origin = d.find('origin')
        if origin is not None:
            self.readOrigin(sm, origin)
        for g in d.find('geometry').getchildren():
            if g.tag == 'mesh':
                sm.shapeType = model.ShapeModel.SP_MESH
                # print "reading mesh " + mesh.attrib['filename']
                filename = utils.resolveFile(g.attrib['filename'])
                fileext = os.path.splitext(filename)[1].lower()
                if fileext == '.dae':
                    reader = collada.ColladaReader()
                else:
                    reader = stl.STLReader()
                sm.data = reader.read(filename, assethandler=self._assethandler)
                try:
                    scales = [float(v) for v in re.split(' +', g.attrib['scale'].strip(' '))]
                    if scales[0] != 0.0:
                        d = model.MeshTransformData()
                        d.matrix = tf.scale_matrix(scales[0])
                        d.children = [sm.data]
                        sm.data = d
                except KeyError:
                    pass
            elif g.tag == 'box':
                sm.shapeType = model.ShapeModel.SP_BOX
                sm.data = model.BoxData()
                boxsize = [float(s) for s in re.split(' +', g.attrib['size'].strip(' '))]
                sm.data.x = boxsize[0]
                sm.data.y = boxsize[1]
                sm.data.z = boxsize[2]
            elif g.tag == 'cylinder':
                sm.shapeType = model.ShapeModel.SP_CYLINDER
                sm.data = model.CylinderData()
                sm.data.radius = float(g.attrib['radius'])
                sm.data.height = float(g.attrib['length'])
            elif g.tag == 'sphere':
                sm.shapeType = model.ShapeModel.SP_SPHERE
                sm.data = model.SphereData()
                sm.data.radius = float(g.attrib['radius'])
            else:
                raise Exception('unsupported shape type: %s' % g.tag)
        return sm


class URDFWriter(object):
    '''
    URDF writer class
    '''
    def write(self, m, f, options=None):
        """Write simulation model in URDF format

        :param m: model data
        :param f: path of the file to save
        :returns: None
        :rtype: None

        """
        # render the data structure using template
        loader = jinja2.PackageLoader(self.__module__, 'template')
        env = jinja2.Environment(loader=loader)

        # render mesh data to each separate collada file
        cwriter = collada.ColladaWriter()
        swriter = stl.STLWriter()
        dirname = os.path.dirname(f)
        for l in m.links:
            for v in l.visuals:
                if v.shapeType == model.ShapeModel.SP_MESH:
                    cwriter.write(v, os.path.join(dirname, v.name + ".dae"))
                    swriter.write(v, os.path.join(dirname, v.name + ".stl"))

        # render model urdf file
        self._convertedjoints = []
        self._convertedlinks = []
        self._roots = utils.findroot(m)
        self._linkmap['world'] = model.LinkModel()
        for l in m.links:
            self._linkmap[l.name] = l
        for root in self._roots:
            self.convertchildren(m, root)
        template = env.get_template('urdf.xml')
        with open(f, 'w') as ofile:
            ofile.write(template.render({
                'model': m,
                'ShapeModel': model.ShapeModel,
                'JointModel': model.JointModel,
                'tf': tf
            }))

    def convertchildren(self, mdata, pjoint):
        children = []
        plink = self._linkmap[pjoint.child]
        for cjoint in utils.findchildren(mdata, pjoint.child):
            nmodel = {}
            try:
                clink = self._linkmap[cjoint.child]
            except KeyError:
                logging.warn("unable to find child link %s" % cjoint.child)
            pjointinv = numpy.linalg.pinv(pjoint.getmatrix())
            cjointinv = numpy.linalg.pinv(cjoint.getmatrix())
            cjoint2 = copy.deepcopy(cjoint)
            cjoint2.matrix = numpy.dot(pjointinv, cjoint.getmatrix())
            cjoint2.trans = None
            cjoint2.rot = None
            clink2 = copy.deepcopy(clink)
            clink2.matrix = numpy.dot(cjointinv, clink.getmatrix())
            clink2.trans = None
            clink2.rot = None
            if not numpy.allclose(clink2.getmatrix(), numpy.identity(4)):
                clink2.translate(clink2.getmatrix())
            self._convertedjoints.append(cjoint2)
            self._convertedlinks.append(clink2)
            self.convertchildren(mdata, cjoint)
