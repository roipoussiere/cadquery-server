import cadquery as cq
from jupyter_cadquery.utils import numpy_to_json
from jupyter_cadquery.cad_objects import to_assembly
from jupyter_cadquery.base import _tessellate_group

def show(model):
    print(numpy_to_json(_tessellate_group(to_assembly(model))))

height = 60.0
width = 80.0
thickness = 10.0
diameter = 22.0
padding = 12.0

model = cq.Workplane("XY").box(height, width, thickness) \
    .faces(">Z").workplane().hole(diameter) \
    .faces(">Z").workplane() \
    .rect(height - padding, width - padding, forConstruction=True) \
    .vertices().cboreHole(2.4, 4.4, 2.1) \
    .edges("|Z").fillet(2.0)

show(model)
