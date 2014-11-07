import os
import sys
from optparse import OptionParser, OptionError

from . import vrml
from . import urdf
from . import sdf
from . import graphviz


def main():
    usage = '''Usage: %prog [options]
Convert robot simulation model from one another.'''
    parser = OptionParser(usage=usage)
    parser.add_option('-i', '--input', dest='fromfile', metavar='FILE', help='convert from FILE')
    parser.add_option('-o', '--output', dest='tofile', metavar='FILE', help='convert to FILE')
    parser.add_option('-f', '--from', dest='fromformat', metavar='FORMAT', help='convert from FORMAT (optional)')
    parser.add_option('-t', '--to', dest='toformat', metavar='FORMAT', help='convert to FORMAT (optional)')
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False, help='verbose output')
    try:
        options, args = parser.parse_args()
    except OptionError, e:
        print >> sys.stderr, 'OptionError: ', e
        print >> sys.stderr, parser.print_help()
        return 1

    if options.tofile is None or options.fromfile is None:
        print >> sys.stderr, parser.print_help()
        return 1

    reader = None
    if options.fromformat == "vrml":
        reader = vrml.VRMLReader()
    if options.fromformat == "urdf":
        reader = urdf.URDFReader()
    if options.fromformat == "sdf":
        reader = sdf.SDFReader()
    if reader is None:
        ext = os.path.splitext(options.fromfile)[1]
        if ext == '.wrl':
            reader = vrml.VRMLReader()
        elif ext == '.urdf':
            reader = urdf.URDFReader()
        elif ext == '.sdf':
            reader = sdf.SDFReader()
        else:
            print >> sys.stderr, 'unable to detect input format (may be not supported?)'
            return 1

    writer = None
    if options.toformat == "vrml":
        writer = vrml.VRMLWriter()
    if options.toformat == "urdf":
        writer = urdf.URDFWriter()
    if options.toformat == "sdf":
        writer = sdf.SDFWriter()
    if options.toformat == "dot":
        writer = graphviz.GraphvizWriter()
    if writer is None:
        ext = os.path.splitext(options.tofile)[1]
        if ext == '.wrl':
            writer = vrml.VRMLWriter()
        elif ext == '.urdf':
            writer = urdf.URDFWriter()
        elif ext == '.sdf':
            writer = sdf.SDFWriter()
        elif ext == '.dot':
            writer = graphviz.GraphvizWriter()
        else:
            print >> sys.stderr, 'unable to detect output format (may be not supported?)'
            return 1

    model = reader.read(options.fromfile)
    writer.write(model, options.tofile)

    return 0

if __name__ == '__main__':
    sys.exit(main())
