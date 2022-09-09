import cadquery as cq
from cq_server.ui import ui, show_object #, debug


box_1 = cq.Workplane('XY').box(1, 2, 3)
box_2 = cq.Workplane('XY').box(3, 2, 1)

show_object(box_1, box_2, options={
    'color': (0, 150, 150),
    'alpha': 0.5
})

# debug(box_1)
