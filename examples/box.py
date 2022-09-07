import cadquery as cq
from cq_server.ui import ui, show_object

height = 60
width = 80
thickness = 10

box = cq.Workplane("XY").box(height, width, thickness)

show_object(box)
