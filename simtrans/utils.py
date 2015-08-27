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
    logger.debug('resolveFile from %s' % f)
    try:
        if f.count('model://') > 0:
            fn = f.replace('model://', '')
            paths = ['.', '~/.gazebo/models']
            for env in ['GAZEBO_MODEL_PATH', 'OPENHRP_MODEL_PATH']:
                try:
                    paths.extend(os.environ[env].split(':'))
                except KeyError:
                    pass
            for p in paths:
                ff = os.path.expanduser(os.path.join(p, fn))
                if os.path.exists(ff):
                    logger.debug('resolveFile resolved to %s' % ff)
                    return ff
        if f.count('package://') > 0:
            pkgname, pkgfile = f.replace('package://', '').split('/', 1)
            ppath = subprocess.check_output(['rospack', 'find', pkgname]).rstrip()
            logger.debug('resolveFile find package path %s' % ppath)
            ff = os.path.join(ppath, pkgfile)
            logger.debug('resolveFile resolved to %s' % ff)
            return ff
    except Exception, e:
        logger.warn(str(e))
    logger.debug('resolveFile unresolved (use original)')
    return f


def findroot(mdata):
    '''
    Find root link from parent to child relationships.
    Currently based on following simple principle:
    - Link with no parent will be the root.

    >>> import subprocess
    >>> from . import urdf
    >>> subprocess.call('rosrun xacro xacro.py `rospack find atlas_description`/robots/atlas_v3.urdf.xacro > /tmp/atlas.urdf', shell=True)
    0
    >>> r = urdf.URDFReader()
    >>> m = r.read('/tmp/atlas.urdf')
    >>> findroot(m)
    ['pelvis']

    >>> from . import urdf
    >>> r = urdf.URDFReader()
    >>> m = r.read('package://ur_description/urdf/ur5_robot.urdf')
    >>> findroot(m)
    ['world']

    >>> import subprocess
    >>> from . import urdf
    >>> subprocess.call('rosrun xacro xacro.py `rospack find pr2_description`/robots/pr2.urdf.xacro > /tmp/pr2.urdf', shell=True)
    0
    >>> r = urdf.URDFReader()
    >>> m = r.read('/tmp/pr2.urdf')
    >>> findroot(m)
    ['base_footprint']

    >>> from . import sdf
    >>> r = sdf.SDFReader()
    >>> m = r.read('model://pr2/model.sdf')
    >>> findroot(m)
    ['base_footprint']
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

    >>> import subprocess
    >>> from . import urdf
    >>> subprocess.call('rosrun xacro xacro.py `rospack find atlas_description`/robots/atlas_v3.urdf.xacro > /tmp/atlas.urdf', shell=True)
    0
    >>> r = urdf.URDFReader()
    >>> m = r.read('/tmp/atlas.urdf')
    >>> [c.child for c in findchildren(m, 'pelvis')]
    ['ltorso', 'l_uglut', 'r_uglut']
    '''
    children = []
    for j in mdata.joints:
        if j.parent == linkname:
            children.append(j)
    return children
