# -*- coding:utf-8 -*-

"""
Numpy port of

Frame transformation functions from
https://bitbucket.org/osrf/sdformat/src/b5ef37039cc7aaf7d3ba69cf30b5be54ec30b8f7/src/parser_urdf.cc
"""

import numpy
import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from . import transformations as tf


def TransformToParentFrame(_transformInLinkFrame, _parentToLinkTransform):
    rot = tf.quaternion_matrix(_parentToLinkTransform.rot)
    trans = rot * _transformInLinkFrame.trans
    rot = tf.quaternion_multiply(_parentToLinkTransform.rot, _transformInLinkFrame.rot)
    trans = _parentToLinkTransform.trans + trans
    return (trans, rot)


def inverseTransformToParentFrame(_transformInLinkFrame, _parentToLinkTransform):
    rot = tf.quaternion_matrix(_parentToLinkTransform.rot)
    ri = numpy.linalg.pinv(rot)
    trans = ri * _transformInLinkFrame.trans
    rot = tf.quaternion_multiply(tf.quaternion_from_matrix(ri), _transformInLinkFrame.rot)
    trans = trans - _parentToLinkTransform.trans
    return (trans, rot)
