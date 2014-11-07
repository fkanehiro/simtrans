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
    >>> resolveFile('model://pr2/model.sdf')
    '/usr/share/gazebo-4.0/models/pr2/model.sdf'
    >>> resolveFile('model://PA10/pa10.main.wrl')
    '/usr/local/share/OpenHRP-3.1/sample/model/PA10/pa10.main.wrl'
    '''
    try:
        if f.count('model://') > 0:
            fn = f.replace('model://', '')
            for env in ['GAZEBO_MODEL_PATH', 'OPENHRP_MODEL_PATH']:
                for p in os.environ[env].split(':'):
                    ff = os.path.join(p, fn)
                    if os.path.exists(ff):
                        return ff
        if f.count('package://') > 0:
            pkgname, pkgfile = f.replace('package://', '').split('/', 1)
            ppath = subprocess.check_output(['rospack', 'find', pkgname]).rstrip()
            return os.path.join(ppath, pkgfile)
    except Exception, e:
        logger.warn(str(e))
    return f
