import collada
m = collada.Collada('./head.dae')

for i in m.images:
    i.path

for g in m.geometries:
    for p in g.primitives:
        p.vertex
        p.normal # vertext normal
        p.material # image used for UV map
        p.texcoordset # UV map
