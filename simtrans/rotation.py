from euclid import *


def vrml_to_q(v):
    axis = Vector3(v[0], v[1], v[2])
    return Quaternion.new_rotate_axis(v[3], axis)

def q_to_vrml(q):
    return q.get_angle_axis()

def q_to_rpy(q):
    pass

def rpy_to_q(rpy):
    q1 = Quaternion.new_rotate_axis(rpy[1], Vector3(0.0, 1.0, 0.0))
    q2 = Quaternion.new_rotate_axis(rpy[0], Vector3(1.0, 0.0, 0.0))
    q3 = Quaternion.new_rotate_axis(rpy[2], Vector3(0.0, 0.0, 1.0))
    return q1 * q2 *q3
