import visvis.vvio.stl


class STLReader:
    def read(self, f):
        r = visvis.vvio.stl.StlReader(None)
        m = r.read(f)
        m._vertices


class STLWriter:
    def write(self, m, f):
        pass
