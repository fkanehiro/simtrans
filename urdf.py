import lxml
d = lxml.etree.parse(open('../urdf/atlas_v3.urdf'))

for l in d.findAll('link'):
    inertia = l.find('inertial')
    visual = l.find('visual')
    collision = l.find('collision')

for j in d.findAll('joint'):
    origin = j.find('origin')
