#!/usr/bin/env python

import sys
from . import vrml

r = vrml.VRMLReader()
m = r.read(sys.argv[1])

print "digraph VRML {"

for j in m.joints:
    print '   %s -> %s [label="%s"]' % (j.parent, j.child, j.name)

print "}"
