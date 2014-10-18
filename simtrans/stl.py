import visvis.vvio.stl
import model


class STLReader:
    def read(self, f):
        m = model.MeshModel
        r = visvis.vvio.stl.StlReader(None)
        p = r.read(f)
        m.vertex = p._vertices
        return m


class STLWriter:
    def write(self, m, f):
        pass
