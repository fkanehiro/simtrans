import lxml


class URDFReader:
    def read(self, f):
        d = lxml.etree.parse(open(f))

        for l in d.findAll('link'):
            inertia = l.find('inertial')
            visual = l.find('visual')
            collision = l.find('collision')

        for j in d.findAll('joint'):
            origin = j.find('origin')


class URDFWriter:
    def write(self, m, f):
        pass
