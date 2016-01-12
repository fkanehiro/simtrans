# -*- coding:utf-8 -*-

"""
Miscellaneous utility functions
"""

import os
import subprocess
import logging


def resolveFile(f):
    '''
    Resolve file by replacing file path heading "package://" or "model://"

    >>> resolveFile('package://atlas_description/package.xml') == os.path.expandvars('$ROS_PACKAGE_PATH/atlas_description/package.xml')
    True
    >>> resolveFile('package://atlas_description/urdf/atlas.urdf') == os.path.expandvars('$ROS_PACKAGE_PATH/atlas_description/atlas.urdf')
    True
    >>> resolveFile('model://pr2/model.sdf') == os.path.expanduser('~/.gazebo/models/pr2/model.sdf')
    True
    >>> resolveFile('model://PA10/pa10.main.wrl') == os.path.expandvars('$OPENHRP_MODEL_PATH/PA10/pa10.main.wrl')
    True
    '''
    logging.debug('resolveFile from %s' % f)
    try:
        if f.count('file://') > 0:
            ff = os.path.expanduser(f.replace('file://', ''))
            if os.path.exists(ff):
                logging.debug('resolveFile resolved to %s' % ff)
                return ff
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
                    logging.debug('resolveFile resolved to %s' % ff)
                    return ff
        if f.count('model://') > 0:
            f = f.replace('model://', 'package://')
        if f.count('package://') > 0:
            pkgname, pkgfile = f.replace('package://', '').split('/', 1)
            ppath = subprocess.check_output(['rospack', 'find', pkgname]).rstrip()
            logging.debug('resolveFile find package path %s' % ppath)
            ff = os.path.join(ppath, pkgfile)
            logging.debug('resolveFile resolved to %s' % ff)
            return ff
    except Exception, e:
        logging.warn(str(e))
    logging.debug('resolveFile unresolved (use original)')
    return f


def findroot(mdata):
    '''
    Find root link from parent to child relationships.
    Currently based on following simple principle:
    - Link with no parent will be the root.
    - Link should have at least one open connection with the other link

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
    peaks = [l[0] for l in sorted(links.items(), key=lambda x: x[1], reverse=True)]
    ret = []
    for p in peaks:
        if hasopenlink(mdata, p):
            ret.append(p)
    for l in mdata.links:
        if not usedlinks.has_key(l.name):
            ret.append(l.name)
    return ret

def hasopenlink(mdata, linkname):
    '''
    Check if the link has open connection with neighboring links

    >>> from . import sdf
    >>> r = sdf.SDFReader()
    >>> m = r.read('model://pr2/model.sdf')
    >>> hasopenlink(m, 'base_footprint')
    True
    >>> hasopenlink(m, 'l_gripper_l_parallel_link')
    False
    '''
    for c in findchildren(mdata, linkname):
        parents = [p.parent for p in findparent(mdata, c.child)]
        if len(set(parents)) == 1:
            return True
    return False


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


def findparent(mdata, linkname):
    '''
    Find parent joints connected to specified link

    >>> import subprocess
    >>> from . import urdf
    >>> subprocess.call('rosrun xacro xacro.py `rospack find atlas_description`/robots/atlas_v3.urdf.xacro > /tmp/atlas.urdf', shell=True)
    0
    >>> r = urdf.URDFReader()
    >>> m = r.read('/tmp/atlas.urdf')
    >>> [p.parent for p in findparent(m, 'ltorso')]
    ['pelvis']
    '''
    parents = []
    for j in mdata.joints:
        if j.child == linkname:
            parents.append(j)
    return parents
