import lxml
import model


class SDFReader:
    def read(self, f):
        d = lxml.etree.parse(open(f))
        m = model.ProjectModel

        for w in d.findAll('world'):
            pass

        for m in d.findAll('model'):
            pass

        return m


class SDFWriter:
    def write(self, m, f):
        pass
