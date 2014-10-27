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
import collada
import jinja2


class ColladaReader(object):
    '''
    Collada reader class
    '''
    def __init__(self):
        self._materials = {}

    def read(self, f):
        '''
        Read collada model data given the file path

        >>> r = ColladaReader()
        >>> m = r.read('/opt/ros/indigo/share/atlas_description/meshes/head.dae')
        '''
        d = collada.Collada(f)
        for m in d.materials:
            self._materials[m.id] = m
        m = model.ShapeModel()
        m.shapeType = model.ShapeModel.SP_NONE
        for n in d.scene.nodes:
            m.children.extend(self.convertchildren(n))
        return m

    def convertchildren(self, d):
        nodes = []
        for c in d.children:
            if type(c) == collada.scene.Node:
                m = model.ShapeModel()
                m.shapeType = model.ShapeModel.SP_NONE
                dmat = tf.decompose_matrix(c.matrix)
                m.scale = dmat[0].tolist()
                m.trans = dmat[3].tolist()
                m.rot = tf.quaternion_from_matrix(tf.compose_matrix(shear=dmat[1], angles=dmat[2]))
                m.children = self.convertchildren(c)
                nodes.append(m)
            elif type(c) == collada.scene.GeometryNode:
                m = model.ShapeModel()
                m.shapeType = model.ShapeModel.SP_MESH
                for p in c.geometry.primitives:
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
                for ml in c.materials:
                    try:
                        for p in self._materials[ml.symbol].effect.params:
                            if type(p) == collada.material.Surface:
                                m.image = p.image.path
                    except KeyError:
                        pass
                nodes.append(m)
        return nodes


class ColladaWriter(object):
    def write(self, m, f):
        pass
