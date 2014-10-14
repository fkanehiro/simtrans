# -*- coding:utf-8 -*-

"""
Reader and writer for collada format
"""

import collada
import model


class ColladaReader:
    def read(self, f):
        m = model.MeshModel
        d = collada.Collada(f)

        for i in d.images:
            i.path
        for g in d.geometries:
            for p in g.primitives:
                m.vertex = p.vertex
                m.vertex_index = p.vertex_index
                m.normal = p.normal
                m.normal_index = p.normal_index
                # m.material = p.material
                # m.uvmap = p.texcoordset
        for e in d.effects:
            e.ambient


class ColladaWriter:
    def write(self, m, f):
        pass
