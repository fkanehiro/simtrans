#!/usr/bin/env python

import sys
import lxml.etree

d = lxml.etree.parse(open(sys.argv[1]))

print "digraph URDF {"

for j in d.findall('joint'):
    parent = j.find('parent').attrib['link']
    child = j.find('child').attrib['link']
    print "   %s -> %s" % (parent, child)

print "}"
