import cadquery as cq

height = 60
width = 80
thickness = 10

result = cq.Workplane("XY").box(height, width, thickness)
