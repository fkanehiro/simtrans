# -*- coding:utf-8 -*-

"""
Reader and writer for VRML format
"""

import jinja2


class VRMLReader:
    '''
    VRML reader class
    '''
    def read(self, f):
        pass


class VRMLWriter:
    '''
    VRML writer class
    '''
    def write(self, m, f):
        env = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))
        template = env.get_template('vrml.wrl')
        of = open(f, 'w')
        of.write(template.render(m))

    def findRoot(self, m):
        '''
        Find a root link from the parent to child relationships.
        Currently based on following simple rule:
        - Link with no parent will be the root.
        '''
        js = {}
        for j in m.joints:
            js[j.parent] = 1
        for j in m.joints:
            try:
                del js[j.child]
            except KeyError:
                pass
