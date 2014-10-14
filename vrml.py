# -*- coding:utf-8 -*-

"""
Reader and writer for VRML format
"""

import jinja2


class VRMLReader:
    def read(self, f):
        pass


class VRMLWriter:
    def write(self, m, f):
        env = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))
        template = env.get_template('vrml.wrl')
        of = open(f, 'w')
        of.write(template.render(m))
