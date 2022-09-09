import cadquery as cq
from cq_server.ui import ui, show_object, debug


wp = cq.Workplane('XY')
box_1 = wp.box(1, 2, 3)
box_2 = wp.box(2, 3, 1)
box_3 = wp.box(3, 1, 2)

show_object(box_1, options={ 'color': (0, 150, 150) })
show_object(box_2, options={ 'color': (150, 0, 150) })
show_object(box_3, options={ 'color': (150, 150, 0) })
debug(wp.box(3.1, 3.1, 3.1))
