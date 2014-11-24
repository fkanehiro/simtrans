# -*- coding:utf-8 -*-

"""simtrans command line interface
"""

import os
import sys
import subprocess
from argparse import ArgumentParser, ArgumentError

from . import vrml
from . import urdf
from . import sdf
from . import graphviz

parser = ArgumentParser(description='Convert robot simulation model from one another.')
parser.add_argument('-i', '--input', dest='fromfile', metavar='FILE', help='convert from FILE')
parser.add_argument('-o', '--output', dest='tofile', metavar='FILE', help='convert to FILE')
parser.add_argument('-f', '--from', dest='fromformat', metavar='FORMAT', help='convert from FORMAT (optional)')
parser.add_argument('-t', '--to', dest='toformat', metavar='FORMAT', help='convert to FORMAT (optional)')
parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False, help='verbose output')


def main():
    try:
        options = parser.parse_args()
    except ArgumentError, e:
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
    handler = None
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
            dirname = os.path.dirname(options.tofile)
            def jpegconvert(f):
                fname = os.path.join(dirname, os.path.splitext(os.path.basename(f))[0] + '.jpg')
                subprocess.check_call(['convert', f, fname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return fname
            handler = jpegconvert
        elif ext == '.urdf':
            writer = urdf.URDFWriter()
        elif ext == '.sdf':
            writer = sdf.SDFWriter()
        elif ext == '.world':
            writer = sdf.SDFWriter()
        elif ext == '.dot':
            writer = graphviz.GraphvizWriter()
        else:
            print >> sys.stderr, 'unable to detect output format (may be not supported?)'
            return 1

    print "converting from: %s" % options.fromfile
    print "             to: %s" % options.tofile

    model = reader.read(options.fromfile, assethandler=handler)
    if len(model.links) == 0:
        print "cannot read links at all (probably the model refers to another model by <include> tag)"
        return 1
    writer.write(model, options.tofile)

    return 0

if __name__ == '__main__':
    sys.exit(main())
