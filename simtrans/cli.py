import sys
from optparse import OptionParser, OptionError

from . import vrml
from . import urdf
from . import sdf

def main():
    usage = '''Usage: %prog [options]
Convert robot simulation model from one another.'''
    parser = OptionParser(usage=usage)
    parser.add_option('-f', '--from', dest='fromformat', metavar='FORMAT', help='from FORMAT')
    parser.add_option('-t', '--to', dest='toformat', metavar='FORMAT', help='to FORMAT')
    parser.add_option('-v', '--verbose', dest='verbose', metavar='FILE', help='verbose output')
    try:
        options, args = parser.parse_args()
    except OptionError, e:
        print >>sys.stderr, 'OptionError: ', e
        return 1

    ret = 0

    if options.fromformat == "vrml":
        reader = vrml.VRMLReader()
    if options.fromformat == "urdf":
        reader = urdf.URDFReader()
    if options.fromformat == "sdf":
        reader = sdf.SDFReader()

    if options.toformat == "vrml":
        writer = vrml.VRMLWriter()

    model = reader.read(args[0])
    writer.write(model, args[1])

    return ret

if __name__ == '__main__':
    sys.exit(main())
