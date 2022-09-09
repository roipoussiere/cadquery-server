import cadquery as cq
from cq_server.ui import ui, show_object, debug


wp = cq.Workplane('XY')
box_r = wp.box(1, 2, 3)
box_g = wp.box(2, 3, 1)
box_b = wp.box(3, 1, 2)

show_object(box_r, name='red box',   options={ 'color': (100, 0, 0) })
show_object(box_g, name='green box', options={ 'color': (0, 100, 0) })
show_object(box_b, name='blue box',  options={ 'color': (0, 0, 100) })
debug(wp.box(3.1, 3.1, 3.1), name='cube')
