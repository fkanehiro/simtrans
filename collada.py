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
                m.normal = p.normal  # vertext normal
                p.material  # image used for UV map
                m.uvmap = p.texcoordset  # UV map


class ColladaWriter:
    def write(self, m, f):
        pass
