# -*- coding:utf-8 -*-

"""
Reader and writer for collada format
"""

from __future__ import absolute_import
from . import model
import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from .thirdparty import transformations as tf
import os
import collada
import numpy
import uuid


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
    def __init__(self):
        self._mesh = None
        self._matnode = None

    def write(self, m, f):
        '''
        Write simulation model in collada format
        '''
        # we use pycollada to generate the dae file
        self._mesh = collada.Collada()

        # create effect and material
        effect = collada.material.Effect("effect0", [], "phong", diffuse=(1,0,0), specular=(0,1,0))
        mat = collada.material.Material("material0", "mymaterial", effect)
        self._mesh.effects.append(effect)
        self._mesh.materials.append(mat)
        self._matnode = collada.scene.MaterialNode("materialref", mat, inputs=[])

        # convert shapes recursively
        node = self.convertchild(m)

        # create scene graph
        myscene = collada.scene.Scene("myscene", [node])
        self._mesh.scenes.append(myscene)
        self._mesh.scene = myscene
        self._mesh.write(f)

    def convertchild(self, m):
        if type(m) == model.NodeModel:
            children = []
            name = 'node-' + str(uuid.uuid1()).replace('-', '')
            for c in m.children:
                cn = self.convertchild(c)
                if cn:
                    children.append(cn)
            node = collada.scene.Node(name, children=children)
            return node
        elif type(m) == model.ShapeModel:
            # append geometric data
            if m.shapeType == model.ShapeModel.SP_MESH:
                name = 'shape-' + str(uuid.uuid1()).replace('-', '')
                vertexname = name + '-vertex'
                normalname = name + '-normal'
                sources = []
                input_list = collada.source.InputList()
                sources.append(collada.source.FloatSource(vertexname, m.data.vertex.reshape(1, m.data.vertex.size), ('X', 'Y', 'Z')))
                indices = m.data.vertex_index.reshape(1, m.data.vertex_index.size)
                input_list.addInput(0, 'VERTEX', '#' + vertexname)
                if m.data.normal:
                    sources.append(collada.source.FloatSource(normalname, m.data.normal.reshape(1, m.data.normal.size), ('X', 'Y', 'Z')))
                    indices = numpy.vstack([indices, m.data.normal_index.reshape(1, m.data.normal_index.size)])
                    input_list.addInput(1, 'NORMAL', '#' + normalname)
                geom = collada.geometry.Geometry(self._mesh, 'geometry0', name, sources)
                # create triangles
                triset = geom.createTriangleSet(indices.T.reshape(1, indices.size), input_list, 'materialref')
                geom.primitives.append(triset)
                self._mesh.geometries.append(geom)
                node = collada.scene.GeometryNode(geom, [self._matnode])
                return node
        return None
