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
import numpy


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
        m = model.NodeModel()
        m.children = []
        for n in d.scene.nodes:
            m.children.append(self.convertchild(n))
        return m

    def convertchild(self, d):
        m = model.NodeModel()
        if type(d) == collada.scene.Node:
            dmat = tf.decompose_matrix(d.matrix)
            m.scale = dmat[0].tolist()
            m.trans = dmat[3].tolist()
            m.rot = tf.quaternion_from_matrix(tf.compose_matrix(shear=dmat[1], angles=dmat[2]))
            m.children = []
            for c in d.children:
                m.children.append(self.convertchild(c))
        elif type(d) == collada.scene.GeometryNode:
            for p in d.geometry.primitives:
                sm = model.ShapeModel()
                sm.shapeType = model.ShapeModel.SP_MESH
                sm.data = model.MeshData()
                sm.data.vertex = p.vertex
                sm.data.vertex_index = p.vertex_index
                if p.normal.size > 0:
                    sm.data.normal = p.normal
                    sm.data.normal_index = p.normal_index
                if len(p.texcoordset) > 0:
                    sm.data.uvmap = p.texcoordset[0]
                    sm.data.uvmap_index = p.texcoord_indexset[0]
                try:
                    for pr in self._materials[p.material].effect.params:
                        if type(pr) == collada.material.Surface:
                            fname = os.path.abspath(os.path.join(self._basepath, pr.image.path))
                            if self._assethandler:
                                sm.image = self._assethandler(fname)
                            else:
                                sm.image = fname
                except KeyError:
                    pass
                m.children.append(sm)
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
        # we use pycollada to generate the dae file
        mesh = collada.Collada()
        # create effect and material
        effect = collada.material.Effect("effect0", [], "phong", diffuse=(1,0,0), specular=(0,1,0))
        mat = collada.material.Material("material0", "mymaterial", effect)
        mesh.effects.append(effect)
        mesh.materials.append(mat)
        # append geometric data
        sources = []
        sources.append(collada.source.FloatSource(m.name+'-vertex', m.vertex, ('X', 'Y', 'Z')))
        sources.append(collada.source.FloatSource(m.name+'-normal', m.normal, ('X', 'Y', 'Z')))
        geom = collada.geometry.Geometry(mesh, 'geometry0', m.name, sources)
        # create triangles
        input_list = collada.source.InputList()
        input_list.addInput(0, 'VERTEX', '#'+m.name+'-vertex')
        input_list.addInput(1, 'NORMAL', '#'+m.name+'-normal')
        # TODO concatinate vertex and normal index
        indices = numpy.array()
        triset = geom.createTriangleSet(indices, input_list, 'materialref')
        geom.primitives.append(triset)
        mesh.geometries.append(geom)
        # create scene graph
        matnode = collada.scene.MaterialNode("materialref", mat, inputs=[])
        geomnode = collada.scene.GeometryNode(geom, [matnode])
        node = collada.scene.Node("node0", children=[geomnode])
        myscene = collada.scene.Scene("myscene", [node])
        mesh.scenes.append(myscene)
        mesh.scene = myscene
        mesh.write(f)
