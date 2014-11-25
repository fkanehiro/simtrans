# -*- coding:utf-8 -*-

"""
Numpy port of

omegaFromRot function from
https://github.com/fkanehiro/openhrp3/blob/master/hrplib/hrpUtil/Eigen3d.cpp

matrix decomposition from writeShape function
https://github.com/fkanehiro/openhrp3/blob/master/server/ModelLoader/VrmlWriter.cpp
"""

import math
import numpy


def omegaFromRot(m):
    '''
    calculate omega values from rotation matrix
    '''
    alpha = (m[0, 0] + m[1, 1] + m[2, 2] - 1.0) / 2.0
    if math.fabs(alpha - 1.0) < 1.0e-6:
        return numpy.array([0, 0, 0])
    else:
        try:
            th = math.acos(alpha)
        except ValueError:
            print "acos value error: %f" % alpha
            if alpha > 0:
                th = 0
            else:
                th = math.pi
        s = math.sin(th)
        if s < numpy.finfo(float).eps:
            return numpy.array([
                math.sqrt((m[0, 0]+1)*0.5)*th,
                math.sqrt((m[1, 1]+1)*0.5)*th,
                math.sqrt((m[2, 2]+1)*0.5)*th
            ])

        k = - 0.5 * th / s

        return numpy.array([
            (m[1, 2] - m[2, 1]) * k,
            (m[2, 0] - m[0, 2]) * k,
            (m[0, 1] - m[1, 0]) * k
        ])


def decomposeMatrix(m):
    '''
    decompose transformation matrix to transform, scale, rotation
    '''
    transform = numpy.array([m[0, 3], m[1, 3], m[2, 3]])
    xaxis = numpy.array([m[0, 0], m[1, 0], m[2, 0]])
    yaxis = numpy.array([m[0, 1], m[1, 1], m[2, 1]])
    zaxis = numpy.array([m[0, 2], m[1, 2], m[2, 2]])
    scale = numpy.array([numpy.linalg.norm(xaxis),
                         numpy.linalg.norm(yaxis),
                         numpy.linalg.norm(zaxis)])
    xaxis = xaxis / scale[0]
    yaxis = yaxis / scale[1]
    zaxis = zaxis / scale[2]
    mm = numpy.matrix([[xaxis[0], yaxis[0], zaxis[0]],
                       [xaxis[1], yaxis[1], zaxis[1]],
                       [xaxis[2], yaxis[2], zaxis[2]]])
    omega = omegaFromRot(mm)
    th = numpy.linalg.norm(omega)
    if th > 1.0e-6:
        axis = [omega/th, th]
    else:
        axis = [[0, 1, 0], 0]
    return (transform, scale, axis)
