# -*- coding:utf-8 -*-

"""submesh extract command (to debug submesh logic)
"""

import os
import sys
import subprocess
from argparse import ArgumentParser, ArgumentError

import numpy

from . import vrml
from . import urdf
from . import sdf
from . import graphviz
from . import collada
from . import model

parser = ArgumentParser(description='Convert robot simulation model from one another.')
parser.add_argument('-i', '--input', dest='fromfile', metavar='FILE', help='convert from FILE')
parser.add_argument('-o', '--output', dest='tofile', metavar='FILE', help='convert to FILE')
parser.add_argument('-t', '--to', dest='toformat', metavar='FORMAT', help='convert to FORMAT (optional)')
parser.add_argument('-s', '--submesh', dest='submesh', metavar='NAME', help='extract submesh NAME')
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

    reader = collada.ColladaReader()

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

    m = model.BodyModel()

    l = model.LinkModel()
    l.name = 'root'
    s = model.ShapeModel()
    s.name = 'visual'
    s.shapeType = model.ShapeModel.SP_MESH
    s.data = reader.read(options.fromfile, submesh=options.submesh, assethandler=handler)
    #tm = model.MeshTransformData()
    #tm.children = [s.data]
    #center = s.data.getcenter()
    #tm.matrix = numpy.identity(4)
    #tm.matrix[0, 3] = -center[0]
    #tm.matrix[1, 3] = -center[1]
    #tm.matrix[2, 3] = -center[2]
    #s.data = tm
    l.visuals = [s]
    m.links.append(l)

    l2 = model.LinkModel()
    l2.name = 'center'
    s2 = model.ShapeModel()
    s2.name = 'center-visual'
    s2.shapeType = model.ShapeModel.SP_SPHERE
    s2.data = model.SphereData()
    s2.data.radius = 0.03
    s2.data.material = model.MaterialModel()
    s2.data.material.diffuse = [1, 0, 0]
    l2.visuals = [s2]
    m.links.append(l2)

    l3 = model.LinkModel()
    l3.name = 'origin'
    s3 = model.ShapeModel()
    s3.name = 'origin-visual'
    s3.shapeType = model.ShapeModel.SP_SPHERE
    s3.data = model.SphereData()
    s3.data.radius = 0.03
    s3.data.material = model.MaterialModel()
    s3.data.material.diffuse = [1, 0, 0]
    l3.visuals = [s3]
    m.links.append(l3)

    l4 = model.LinkModel()
    l4.name = 'max'
    s4 = model.ShapeModel()
    s4.name = 'max-visual'
    s4.shapeType = model.ShapeModel.SP_SPHERE
    s4.data = model.SphereData()
    s4.data.radius = 0.03
    s4.data.material = model.MaterialModel()
    s4.data.material.diffuse = [1, 0, 0]
    l4.visuals = [s4]
    m.links.append(l4)

    l5 = model.LinkModel()
    l5.name = 'min'
    s5 = model.ShapeModel()
    s5.name = 'min-visual'
    s5.shapeType = model.ShapeModel.SP_SPHERE
    s5.data = model.SphereData()
    s5.data.radius = 0.03
    s5.data.material = model.MaterialModel()
    s5.data.material.diffuse = [1, 0, 0]
    l5.visuals = [s5]
    m.links.append(l5)

    j = model.JointModel()
    j.parent = 'world'
    j.child = l.name
    j.name = j.parent + j.child
    j.jointType = model.JointModel.J_FIXED
    m.joints.append(j)

    j2 = model.JointModel()
    j2.parent = 'world'
    j2.child = l2.name
    j2.name = j2.parent + j2.child
    j2.jointType = model.JointModel.J_FIXED
    j2.trans = s.data.getcenter()
    m.joints.append(j2)

    j3 = model.JointModel()
    j3.parent = 'world'
    j3.child = l3.name
    j3.name = j3.parent + j3.child
    j3.jointType = model.JointModel.J_FIXED
    m.joints.append(j3)

    j4 = model.JointModel()
    j4.parent = 'world'
    j4.child = l4.name
    j4.name = j4.parent + j4.child
    j4.jointType = model.JointModel.J_FIXED
    j4.trans = s.data.maxv()[0:3]
    m.joints.append(j4)

    j5 = model.JointModel()
    j5.parent = 'world'
    j5.child = l5.name
    j5.name = j5.parent + j5.child
    j5.jointType = model.JointModel.J_FIXED
    j5.trans = s.data.minv()[0:3]
    m.joints.append(j5)

    writer.write(m, options.tofile)

    return 0

if __name__ == '__main__':
    sys.exit(main())
