import lxml


class SDFReader:
    def read(self, f):
        d = lxml.etree.parse(open(f))

        for w in d.findAll('world'):
            pass

        for m in d.findAll('model'):
            pass


class SDFWriter:
    def write(self, m, f):
        pass
