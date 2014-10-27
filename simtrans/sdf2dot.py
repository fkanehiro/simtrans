#!/usr/bin/env python

import sys
import lxml.etree

d = lxml.etree.parse(open(sys.argv[1]))

print "digraph SDF {"

for j in d.find('model').findall('joint'):
    jtype = j.attrib['type']
    jname = j.attrib['name']
    parent = j.find('parent').text
    child = j.find('child').text
    print '   %s -> %s [label="%s:%s"]' % (parent, child, jname, jtype)

print "}"
