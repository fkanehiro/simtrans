# -*- coding:utf-8 -*-

"""
Reader and writer for collada format
"""

from __future__ import absolute_import
from . import model
try:
    from .thirdparty import transformations as tf
except UserWarning:
    pass
import os
import collada
import jinja2


class ColladaReader(object):
    '''
    Collada reader class
    '''
    def __init__(self):
        self._basepath = None
        self._assethandler = None
        self._materials = {}

    def read(self, f, assethandler=None):
        '''
        Read collada model data given the file path

        >>> r = ColladaReader()
        >>> m = r.read('/opt/ros/indigo/share/atlas_description/meshes/head.dae')
        '''
        self._basepath = os.path.dirname(f)
        self._assethandler = assethandler
        d = collada.Collada(f)
        for m in d.materials:
            self._materials[m.id] = m
        m = model.ShapeModel()
        m.shapeType = model.ShapeModel.SP_NONE
        m.children = []
        for n in d.scene.nodes:
            m.children.append(self.convertchild(n))
        return m

    def convertchild(self, d):
        m = None
        if type(d) == collada.scene.Node:
            m = model.ShapeModel()
            m.shapeType = model.ShapeModel.SP_NONE
            dmat = tf.decompose_matrix(d.matrix)
            m.scale = dmat[0].tolist()
            m.trans = dmat[3].tolist()
            m.rot = tf.quaternion_from_matrix(tf.compose_matrix(shear=dmat[1], angles=dmat[2]))
            m.children = []
            for c in d.children:
                m.children.append(self.convertchild(c))
        elif type(d) == collada.scene.GeometryNode:
            m = model.ShapeModel()
            m.shapeType = model.ShapeModel.SP_MESH
            for p in d.geometry.primitives:
                gm = model.MeshModel()
                gm.vertex = p.vertex
                gm.vertex_index = p.vertex_index
                if p.normal.size > 0:
                    gm.normal = p.normal
                    gm.normal_index = p.normal_index
                if len(p.texcoordset) > 0:
                    gm.uvmap = p.texcoordset[0]
                    gm.uvmap_index = p.texcoord_indexset[0]
                m.children.append(gm)
                try:
                    for pr in self._materials[p.material].effect.params:
                        if type(pr) == collada.material.Surface:
                            fname = os.path.abspath(os.path.join(self._basepath, pr.image.path))
                            if self._assethandler:
                                m.image = self._assethandler(fname)
                            else:
                                m.image = fname
                except KeyError:
                    pass
        return m


class ColladaWriter(object):
    '''
    Collada writer class
    '''
    def write(self, m, f):
        '''
        Write simulation model in collada format
        '''
        if type(m) != model.MeshModel:
            raise Exception('collada format can only be used to store mesh model')
        # render the data structure using template
        loader = jinja2.PackageLoader(self.__module__, 'template')
        env = jinja2.Environment(loader=loader)

        # render mesh collada file for each links
        template = env.get_template('collada-mesh.dae')
        with open(f, 'w') as ofile:
            ofile.write(template.render({
                'model': m,
                'ShapeModel': model.ShapeModel,
                'tf': tf
            }))
