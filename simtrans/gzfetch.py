# -*- coding:utf-8 -*-

"""Utility command to fetch simulation model from gazebo's model database
"""

import os
import sys
from optparse import OptionParser, OptionError
import subprocess
import tempfile
import jinja2


def renderworld(models):
    fd, worldfile = tempfile.mkstemp(suffix='.world')
    os.close(fd)
    with open(worldfile, 'w') as ofile:
        ofile.write(jinja2.Template('''<?xml version="1.0" ?>
<sdf version="1.5">
  <world name="default">
{%- for m in models %}
    <include>
      <uri>model://{{m}}</uri>
    </include>
{%- endfor %}
  </world>
</sdf>
''').render({'models': models}))
    return worldfile


def main():
    usage = '''Usage: %prog [options] model://name
Utility command to fetch simulation model from gazebo's model database.'''
    parser = OptionParser(usage=usage)
    parser.add_option('-f', '--fromfile', dest='fromfile', metavar='FILE', help='read list from FILE (optional)')
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False, help='verbose output')
    try:
        options, args = parser.parse_args()
    except OptionError, e:
        print >> sys.stderr, 'OptionError: ', e
        print >> sys.stderr, parser.print_help()
        return 1

    if options.fromfile is None and len(args) == 0:
        print >> sys.stderr, parser.print_help()
        return 1

    # prepare world file which contains required model information
    worldfile = None
    needcleanup = False
    if options.fromfile:
        models = [f.rstrip() for f in open(options.fromfile).readlines()]
        worldfile = renderworld(models)
        needcleanup = True
    elif args[0].count('.world'):
        worldfile = args[0]
    else:
        worldfile = renderworld(args)
        needcleanup = True

    # now fetch the simulation model (run gzserver for only one iteration)
    print "running gzserver to fetch the models ... (this will take a while)"
    subprocess.check_output(['gzserver', '--iters', '1', worldfile])
    print "done!"

    if needcleanup:
        os.unlink(worldfile)

    return 0

if __name__ == '__main__':
    sys.exit(main())
