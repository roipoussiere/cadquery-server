import cadquery as cq
from cq_server.ui import ui, show_object #, debug


height = 60
width = 80
thickness = 10

box = cq.Workplane('XY').box(height, width, thickness)

show_object(box, options={
    'color': (50, 100, 150),
    'alpha': 0.5
})

# debug(box)
