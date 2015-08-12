# -*- coding:utf-8 -*-

"""simtrans command line interface
"""

import os
import sys
import subprocess
import shutil
import logging
try:
    import coloredlogs
    coloredlogs.install(show_hostname=False, show_name=False)
except ImportError:
    print 'unable to find python coloredlogs library.'
    print 'please install by following command to get fancy output:'
    print '$ sudo pip install coloredlogs'
    pass

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


basedir = ''


def jpegconverthandler(f):
    global basedir
    fname = os.path.join(basedir, os.path.splitext(os.path.basename(f))[0] + '.jpg')
    try:
        subprocess.check_call(['convert', f, fname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        logging.error('Unable to find imagemagick "convert" command.')
        logging.error('Please install imagemagick package by:')
        logging.error('$ sudo apt-get install imagemagick')
        raise
    return os.path.relpath(fname, basedir)


def copyhandler(f):
    global basedir
    fname = os.path.join(basedir, os.path.basename(f))
    shutil.copyfile(f, fname)
    return os.path.relpath(fname, basedir)


def main():
    global basedir
    try:
        options = parser.parse_args()
    except ArgumentError, e:
        logging.error('OptionError: ', e)
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
            logging.error('unable to detect input format (may be not supported?)')
            return 1

    basedir = os.path.dirname(os.path.abspath(options.tofile))
    writer = None
    handler = copyhandler
    if options.toformat == "vrml":
        writer = vrml.VRMLWriter()
        handler = jpegconverthandler
    if options.toformat == "urdf":
        writer = urdf.URDFWriter()
    if options.toformat == "sdf":
        writer = sdf.SDFWriter()
    if options.toformat == "dot":
        writer = graphviz.GraphvizWriter()
        handler = None
    if writer is None:
        ext = os.path.splitext(options.tofile)[1]
        if ext == '.wrl':
            writer = vrml.VRMLWriter()
            handler = jpegconverthandler
        elif ext == '.urdf':
            writer = urdf.URDFWriter()
        elif ext == '.sdf':
            writer = sdf.SDFWriter()
        elif ext == '.world':
            writer = sdf.SDFWriter()
        elif ext == '.dot':
            writer = graphviz.GraphvizWriter()
            handler = None
        else:
            logging.error('unable to detect output format (may be not supported?)')
            return 1

    logging.info("converting from: %s" % options.fromfile)
    logging.info("             to: %s" % options.tofile)

    model = reader.read(options.fromfile, assethandler=handler)
    if len(model.links) == 0:
        logging.error("cannot read links at all (probably the model refers to another model by <include> tag)")
        return 1
    writer.write(model, options.tofile)

    return 0

if __name__ == '__main__':
    sys.exit(main())
