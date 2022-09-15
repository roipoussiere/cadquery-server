import cadquery as cq
from cq_server.ui import ui, show_object, debug


wp = cq.Workplane('XY')

asm = ( cq.Assembly(name='assembly')
    .add(wp.box(1, 2, 3), name='red box')
    .add(wp.box(2, 3, 1), name='green box', color=cq.Color('green'))
    .add(wp.box(3, 1, 2), name='blue box', color=cq.Color('blue'))
)

show_object(asm, options={ 'color': cq.Color('red') })
debug(wp.box(3.1, 3.1, 3.1), name='cube')
