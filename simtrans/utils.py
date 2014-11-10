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
                paths.extend(os.environ[env].split(':'))
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
