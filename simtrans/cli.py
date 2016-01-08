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

from ._version import get_versions
__version__ = get_versions()['version']

from . import model
from . import vrml
from . import urdf
from . import sdf
from . import collada
from . import stl
from . import graphviz
from . import utils

logging.info("simtrans (version %s)" % __version__)

parser = ArgumentParser(description='Convert robot simulation model from one another.')
parser.add_argument('-i', '--input', dest='fromfile', metavar='FILE', help='convert from FILE')
parser.add_argument('-o', '--output', dest='tofile', metavar='FILE', help='convert to FILE')
parser.add_argument('-f', '--from', dest='fromformat', metavar='FORMAT', help='convert from FORMAT (optional)')
parser.add_argument('-c', '--use-collision', action='store_true', dest='usecollision', default=False, help='use collision shape when converting to VRML')
parser.add_argument('-b', '--use-both', action='store_true', dest='useboth', default=False, help='use both visual and collision shape when converting to VRML (only supported on most recent version of Choreonoid)')
parser.add_argument('-t', '--to', dest='toformat', metavar='FORMAT', help='convert to FORMAT (optional)')
parser.add_argument('-p', '--prefix', dest='prefix', metavar='PREFIX', default='', help='prefix given to mesh path (e.g. package://packagename, optional)')
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

    if options.verbose:
        logging.info('enable verbose output')
        logging.level = logging.DEBUG
        if 'coloredlogs' in dir():
            coloredlogs.set_level(logging.DEBUG)

    if options.tofile is None or options.fromfile is None:
        print >> sys.stderr, parser.print_help()
        return 1

    options.tofile = os.path.abspath(utils.resolveFile(options.tofile))
    options.fromfile = os.path.abspath(utils.resolveFile(options.fromfile))
    
    reader = None
    meshinput = False
    if options.fromformat == "vrml":
        reader = vrml.VRMLReader()
    if options.fromformat == "urdf":
        reader = urdf.URDFReader()
    if options.fromformat == "sdf":
        reader = sdf.SDFReader()
    if options.fromformat == "collada":
        reader = collada.ColladaReader()
        meshinput = True
    if options.fromformat == "stl":
        reader = stl.STLReader()
        meshinput = True
    if reader is None:
        ext = os.path.splitext(options.fromfile)[1]
        if ext == '.wrl':
            reader = vrml.VRMLReader()
        elif ext == '.urdf':
            reader = urdf.URDFReader()
        elif ext == '.sdf':
            reader = sdf.SDFReader()
        elif ext == '.dae':
            reader = collada.ColladaReader()
            meshinput = True
        elif ext == '.stl':
            reader = stl.STLReader()
            meshinput = True
        else:
            logging.error('unable to detect input format (may be not supported?)')
            return 1

    basedir = os.path.dirname(os.path.abspath(options.tofile))
    writer = None
    handler = copyhandler
    meshoutput = False
    if options.toformat == "vrml":
        if meshinput:
            writer = vrml.VRMLMeshWriter()
            meshoutput = True
        else:
            writer = vrml.VRMLWriter()
        handler = jpegconverthandler
    if options.toformat == "urdf":
        writer = urdf.URDFWriter()
    if options.toformat == "sdf":
        writer = sdf.SDFWriter()
    if options.toformat == "dot":
        writer = graphviz.GraphvizWriter()
        handler = None
    if options.toformat == "collada":
        writer = collada.ColladaWriter()
        meshoutput = True
    if options.toformat == "stl":
        writer = stl.STLWriter()
        handler = None
        meshoutput = True
    if writer is None:
        ext = os.path.splitext(options.tofile)[1]
        if ext == '.wrl':
            if meshinput:
                writer = vrml.VRMLMeshWriter()
                meshoutput = True
            else:
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
        elif ext == '.dae':
            writer = collada.ColladaWriter()
            meshoutput = True
        elif ext == '.stl':
            writer = stl.STLWriter()
            meshoutput = True
        else:
            logging.error('unable to detect output format (may be not supported?)')
            return 1

    logging.info("converting from: %s" % options.fromfile)
    logging.info("             to: %s" % options.tofile)

    m = reader.read(options.fromfile, assethandler=handler, options=options)

    if meshinput:
        nm = model.BodyModel()
        nl = model.LinkModel()
        ns = model.ShapeModel()
        ns.shapeType = model.ShapeModel.SP_MESH
        ns.data = m
        nl.visuals.append(ns)
        nm.links.append(nl)
        m = nm
        
    if len(m.links) == 0:
        logging.error("cannot read links at all (probably the model refers to another model by <include> tag or <link> tag contains no <inertial> or <visual> or <collision> item and reduced by simulation optimization process of gz command used inside simtrans)")
        return 1

    if meshoutput:
        m = m.links[0].visuals[0]

    writer.write(m, options.tofile, options=options)

    return 0

if __name__ == '__main__':
    sys.exit(main())
