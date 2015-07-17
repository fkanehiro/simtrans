# -*- coding:utf-8 -*-

"""
Miscellaneous utility functions
"""

import os
import subprocess
from logging import getLogger
logger = getLogger(__name__)


def resolveFile(f):
    '''
    Resolve file by replacing file path heading "package://" or "model://"

    >>> resolveFile('package://atlas_description/package.xml')
    '/opt/ros/indigo/share/atlas_description/package.xml'
    >>> resolveFile('package://atlas_description/urdf/atlas.urdf')
    '/opt/ros/indigo/share/atlas_description/urdf/atlas.urdf'
    >>> resolveFile('model://pr2/model.sdf') == os.path.expanduser('~/.gazebo/models/pr2/model.sdf')
    True
    >>> resolveFile('model://PA10/pa10.main.wrl') == os.path.expandvars('$OPENHRP_MODEL_PATH/PA10/pa10.main.wrl')
    True
    '''
    try:
        if f.count('model://') > 0:
            fn = f.replace('model://', '')
            paths = ['~/.gazebo/models']
            for env in ['GAZEBO_MODEL_PATH', 'OPENHRP_MODEL_PATH']:
                try:
                    paths.extend(os.environ[env].split(':'))
                except KeyError:
                    pass
            for p in paths:
                ff = os.path.expanduser(os.path.join(p, fn))
                if os.path.exists(ff):
                    return ff
        if f.count('package://') > 0:
            pkgname, pkgfile = f.replace('package://', '').split('/', 1)
            ppath = subprocess.check_output(['rospack', 'find', pkgname]).rstrip()
            return os.path.join(ppath, pkgfile)
    except Exception, e:
        logger.warn(str(e))
    return f


def findroot(mdata):
    '''
    Find root link from parent to child relationships.
    Currently based on following simple principle:
    - Link with no parent will be the root.

    >>> from . import urdf
    >>> r = urdf.URDFReader()
    >>> m = r.read('package://atlas_description/urdf/atlas_v3.urdf')
    >>> findroot(m)[0]
    'pelvis'

    >>> from . import urdf
    >>> r = urdf.URDFReader()
    >>> m = r.read('package://ur_description/urdf/ur5_robot.urdf')
    >>> findroot(m)[0]
    'world'

    >>> from . import sdf
    >>> r = sdf.SDFReader()
    >>> m = r.read('model://pr2/model.sdf')
    >>> findroot(m)[0]
    'base_footprint'
    '''
    links = {}
    usedlinks = {}
    for j in mdata.joints:
        try:
            links[j.parent] = links[j.parent] + 1
        except KeyError:
            links[j.parent] = 1
        usedlinks[j.parent] = True
        usedlinks[j.child] = True
    for j in mdata.joints:
        try:
            del links[j.child]
        except KeyError:
            pass
    ret = [l[0] for l in sorted(links.items(), key=lambda x: x[1], reverse=True)]
    for l in mdata.links:
        if not usedlinks.has_key(l.name):
            ret.append(l.name)
    return ret


def findchildren(mdata, linkname):
    '''
    Find child joints connected to specified link

    >>> from . import urdf
    >>> r = urdf.URDFReader()
    >>> m = r.read('package://atlas_description/urdf/atlas_v3.urdf')
    >>> w = VRMLWriter()
    >>> [c.child for c in w.findchildren(m, 'pelvis')]
    ['ltorso', 'l_uglut', 'r_uglut']
    '''
    children = []
    for j in mdata.joints:
        if j.parent == linkname:
            children.append(j)
    return children
