# -*- coding:utf-8 -*-

"""Reader and writer for Choreonoid body format

:Organization:
 MID

Requirements
------------
* numpy
* yaml
* jinja2 template engine

Examples
--------

Read body model data given the file path

>>> r = CnoidBodyReader()
>>> m = r.read(os.path.expandvars('$OPENHRP_MODEL_PATH/closed-link-sample.wrl'))
"""

from . import model
from . import utils
from . import collada
from . import stl
import os
import sys
import time
import logging
import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from .thirdparty import transformations as tf
import math
import numpy
import copy
import jinja2
import uuid
import yaml

class CnoidBodyReader(object):
    '''
    Choreonoid body reader class
    '''
    def __init__(self):
        self._model = None
        self._linknamemap = {}
        self._assethandler = None
        self._to_radian = lambda x: x
        self._rel_poses = {}

    def dict_to_list(self, es):
        if type(es) == dict:
            r = []
            for (k, v) in es.items():
                v['type'] = k
                r.append(v)
            return r
        return es

    def read(self, f, assethandler=None, options=None):
        '''
        Read Choreonoid body model data given the file path
        '''
        self._assethandler = assethandler
        modeldata = open(f, 'r').read()
        try:
            self._model = yaml.load(modeldata)
        except yaml.scanner.ScannerError:
            # fallback for ScannerError (some choreonoid model contains invalid tab characters)
            self._model = yaml.load(modeldata.replace("\t", ''))

        if self._model['format'] != 'ChoreonoidBody':
            raise yaml.scanner.ScannerError('This file is not ChoreonoidBody format')

        if self._model['angleUnit'] == 'degree':
            self._to_radian = math.radians

        context = {}
        bm = model.BodyModel()
        bm.name = self._model['name']
        context['body'] = bm
        context['trans'] = model.TransformationModel().getmatrix()

        # 1st step: read links in relative frame
        for l in self.dict_to_list(self._model['links']):
            try:
                if l['type'] == 'Skip':
                    continue
            except KeyError:
                pass

            lm = self.readLink(l, context)
            bm.links.append(lm)
            if lm.name == self._model['rootLink']:
                if l['jointType'] == 'fixed':
                    j = model.JointModel()
                    j.jointType = model.JointModel.J_FIXED
                    j.child = lm.name
                    j.parent = 'world'
                    j.name = j.parent + '-' + j.child
                    bm.joints.append(j)
                self._linknamemap[lm.name] = (lm, None)
            else:
                jm = self.readJoint(l)
                bm.joints.append(jm)
                self._linknamemap[lm.name] = (lm, jm)

            # read poses in relative corrdinate (later convert to absolute)
            p = model.TransformationModel()
            try:
                p.trans = numpy.array(l['translation'])
            except KeyError:
                pass
            try:
                r = l['rotation']
                p.rot = tf.quaternion_about_axis(self._to_radian(r[3]), r[0:3])
            except KeyError:
                pass
            self._rel_poses[lm.name] = p

        # set jointId (only used in VRML model)
        for i, j in enumerate(bm.joints):
            j.jointId = i

        # 2nd step: convert to absolute corrdinate
        rootname = self._model['rootLink']
        rootpose = self._rel_poses[rootname].getmatrix()
        rootlink = self._linknamemap[rootname][0]
        for c in self._linknamemap.keys():
            (lm2, jm2) = self._linknamemap[c]
            if jm2 and jm2.parent == rootname:
                self.relToAbs(rootpose, c)
        # TODO: need to translate CoM and inertia here
        for v in rootlink.visuals:
            v.matrix = numpy.dot(rootpose, v.getmatrix())
            v.trans = None
            v.rot = None
        for c in rootlink.collisions:
            c.matrix = numpy.dot(rootpose, c.getmatrix())
            c.trans = None
            c.rot = None

        return bm

    def relToAbs(self, absparent, childname):
        relchild = self._rel_poses[childname]
        (lm, jm) = self._linknamemap[childname]

        # convert to absolute position
        abschild = numpy.dot(absparent, relchild.getmatrix())

        jm.matrix = abschild
        jm.trans = None
        jm.rot = None
        lm.matrix = abschild
        lm.trans = None
        lm.rot = None

        for c in self._linknamemap.keys():
            (lm2, jm2) = self._linknamemap[c]
            if jm2 and jm2.parent == childname:
                self.relToAbs(abschild, c)

    def readJoint(self, m):
        name = m['name']
        j = model.JointModel()
        j.child = m['name']

        # read joint info
        j.child = name
        j.parent = m['parent']
        j.axis = model.AxisData()
        try:
            v = m['jointRange']
            if type(v) == str and v == 'unlimited':
                pass
            else:
                j.axis.limit = [v[1], v[0]]
        except KeyError:
            pass
        try:
            v = float(m['maxJointVelocity'])
            j.axis.velocitylimit = [v, -v]
        except KeyError:
            pass
        try:
            v = m['jointMotorForceRange']
            j.axis.effortlimit = [v[1], v[0]]
        except KeyError:
            pass
        try:
            v = m['jointAxis']
            if v == 'X':
                j.axis.axis = [0, 0, 1]
            elif v == 'Y':
                j.axis.axis = [0, 1, 0]
            elif v == 'Z':
                j.axis.axis = [1, 0, 0]
        except KeyError:
            pass
        t = m['jointType']
        if t == 'fixed':
            j.jointType = model.JointModel.J_FIXED
        elif t == 'rotate':
            if j.axis.limit is None or (j.axis.limit[0] is None and j.axis.limit[1] is None):
                j.jointType = model.JointModel.J_CONTINUOUS
            else:
                j.jointType = model.JointModel.J_REVOLUTE
        elif t == 'revolute':
            j.jointType = model.JointModel.J_REVOLUTE
        elif t == 'slide':
            j.jointType = model.JointModel.J_PRISMATIC
        elif t == 'crawler':
            j.jointType = model.JointModel.J_CRAWLER
        elif t == 'pseudoContinuousTrack':
            j.jointType = model.JointModel.J_CRAWLER
        else:
            raise Exception('unsupported joint type: %s' % t)

        j.name = j.parent + '-' + j.child
        return j

    def readLink(self, m, context):
        lm = model.LinkModel()
        lm.name = m['name']
        try:
            lm.mass = m['mass']
        except KeyError:
            lm.mass = 0.000001
        try:
            lm.centerofmass = numpy.array([float(v) for v in m['centerOfMass']])
        except KeyError:
            pass
        try:
            lm.inertia = numpy.array([float(v) for v in m['inertia']]).reshape(3, 3)
        except KeyError:
            pass
        lm.visuals = []
        lm.collisions = []
        context['link'] = lm
        for e in self.dict_to_list(m['elements']):
            self.readItem(e, context)
        for i, v in enumerate(lm.visuals):
            v.name = lm.name + '-visual-' + str(i)
        for i, c in enumerate(lm.collisions):
            c.name = lm.name + '-collision-' + str(i)
        return lm

    def readItem(self, e, context):
        t = e['type']
        if t == 'Skip':
            return
        elif t == 'Transform' or t == 'RigidBody':
            tm = model.TransformationModel()
            try:
                tm.trans = numpy.array(e['translation'])
            except KeyError:
                pass
            try:
                r = e['rotation']
                tm.rot = tf.quaternion_about_axis(self._to_radian(r[3]), r[0:3])
            except KeyError:
                pass
            trans = context['trans']
            for ce in self.dict_to_list(e['elements']):
                context['trans'] = numpy.dot(trans, tm.getmatrix())
                self.readItem(ce, context)
            context['trans'] = trans
        elif t == 'Visual':
            context['shapeType'] = 'visual'
            try:
                for ce in self.dict_to_list(e['elements']):
                    self.readItem(ce, context)
            except KeyError:
                ce = e['shape']
                ce['type'] = 'Shape'
                self.readItem(ce, context)
        elif t == 'Collision':
            context['shapeType'] = 'collision'
            for ce in self.dict_to_list(e['elements']):
                self.readItem(ce, context)
        #elif t == 'RigidBody':
        #    lm = context['link']
        #    clm = self.readLink(e, context)
        #    context['body'].links.append(clm)
        #    cjm = model.JointModel()
        #    cjm.parent = lm.name
        #    cjm.child = clm.name
        #    cjm.name = cjm.parent + '-' + cjm.child
        #    cjm.jointType = model.JointModel.J_FIXED
        #    context['body'].joints.append(cjm)
        #    self._linknamemap[clm.name] = (clm, cjm)
        #    context['link'] = lm
        elif t == 'Shape':
            sm = model.ShapeModel()
            tm = model.TransformationModel()
            try:
                tm.trans = numpy.array(e['translation'])
            except KeyError:
                pass
            try:
                r = e['rotation']
                tm.rot = tf.quaternion_about_axis(self._to_radian(r[3]), r[0:3])
            except KeyError:
                pass
            sm.matrix = numpy.dot(context['trans'], tm.getmatrix())
            sm.trans = None
            sm.rot = None
            t = e['geometry']['type']
            if t == 'Resource':
                sm.shapeType = model.ShapeModel.SP_MESH
                filename = utils.resolveFile(e['geometry']['uri'])
                fileext = os.path.splitext(filename)[1].lower()
                if fileext == '.dae':
                    reader = collada.ColladaReader()
                else:
                    reader = stl.STLReader()
                    sm.data = reader.read(filename, assethandler=self._assethandler)
            elif t == 'Sphere':
                sm.shapeType = model.ShapeModel.SP_SPHERE
                sm.data = model.SphereData()
                sm.data.radius = e['geometry']['radius']
            elif t == 'Cylinder':
                sm.shapeType = model.ShapeModel.SP_CYLINDER
                sm.data = model.CylinderData()
                sm.data.radius = e['geometry']['radius']
                sm.data.height = e['geometry']['height']
            elif t == 'Box':
                sm.shapeType = model.ShapeModel.SP_BOX
                sm.data = model.BoxData()
                s = e['geometry']['size']
                sm.data.x = s[0]
                sm.data.y = s[1]
                sm.data.z = s[2]
            try:
                mtd = e['appearance']['material']
                mt = model.MaterialModel()
                try:
                    mt.diffuse = mtd['diffuseColor'] + [1.0]
                except KeyError:
                    pass
                try:
                    mt.specular = mtd['specularColor'] + [1.0]
                except KeyError:
                    pass
                try:
                    mt.shininess = mtd['shininess']
                except KeyError:
                    pass
                sm.data.material = mt
            except KeyError:
                pass
            if context['shapeType'] == 'visual':
                context['link'].visuals.append(sm)
            else:
                context['link'].collisions.append(sm)
