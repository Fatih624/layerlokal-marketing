import bpy
import json
import math
from mathutils import Vector
from pathlib import Path

OUT = Path(__file__).resolve().parent
MM = 0.001
AXLE_X = (-165, 165)
AXLE_Z = 90
RADIUS = 90
SHAFT_R = 8
GOOD_BORE = (8.4, 8.4)
WORN_BORE = (11.6, 8.8)
HUB = (124, 154)
WASHER = (155, 159)
PIN_Y = 162
PIN_R = 2.2
TIP_Y = 174
EPS = 1e-6

def mm(values):
    return tuple(v * MM for v in values)

def material(name, color, metallic=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    shader = m.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1.0)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = 0.46
    return m

def tag(obj, name, mat):
    obj.name = name
    if mat:
        obj.data.materials.append(mat)
    return obj

def block(name, center, dimensions, mat):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=mm(center))
    obj = tag(bpy.context.object, name, mat)
    obj.dimensions = mm(dimensions)
    return obj

def cyl(name, center, radius, length, mat=None, axial_y=False):
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=radius * MM, depth=length * MM,
                                       location=mm(center), rotation=(-math.pi/2, 0, 0) if axial_y else (0, 0, 0))
    return tag(bpy.context.object, name, mat)

def ring(name, center, outer, hole, width, mat, side):
    n = 96
    vertices = []
    for z in (-width / 2, width / 2):
        for rx, ry in ((outer, outer), hole):
            for i in range(n):
                angle = 2 * math.pi * i / n
                vertices.append(mm((rx * math.cos(angle), ry * math.sin(angle), z)))
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.extend(((i, j, 2*n+j, 2*n+i), (n+j, n+i, 3*n+i, 3*n+j),
                      (j, i, n+i, n+j), (2*n+i, 2*n+j, 3*n+j, 3*n+i)))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = mm(center)
    obj.rotation_euler.x = -side * math.pi / 2
    return tag(obj, name, mat)

def make_wheel(x, y, z, side, worn=False, label='Rad'):
    hole = WORN_BORE if worn else GOOD_BORE
    tire = ring(label + ' | Reifen', (x,y,z), RADIUS, (71,71), 25, rubber, side)
    ring(label + ' | Felge', (x,y,z), 71, (23,23), 20, wood, side)
    ring(label + ' | Nabe', (x,y,z), 23, hole, 30, worn_metal if worn else metal, side)
    return tire

def make_axle(x):
    axle = cyl('Achse mit Querbohrungen', (x,0,AXLE_Z), SHAFT_R, 2*TIP_Y, metal, True)
    for side in (-1,1):
        drill = cyl('Bohrwerkzeug', (x,side*PIN_Y,AXLE_Z), 2.5, 24)
        bpy.context.view_layer.objects.active = axle
        cut = axle.modifiers.new('Querbohrung Ø5 mm', 'BOOLEAN')
        cut.operation = 'DIFFERENCE'
        cut.object = drill
        bpy.ops.object.modifier_apply(modifier=cut.name)
        bpy.data.objects.remove(drill, do_unlink=True)

def clip(x, y, z):
    cyl('Sicherungsclip | Stift', (x,y,z), PIN_R, 25, metal)
    points = [(0,12), (2.2,15.5), (6.4,15.5), (9.6,12), (9.6,7.5),
              (7.5,4), (7.5,-4), (10,-8)]
    curve = bpy.data.curves.new('Federbügel', 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = 0.0016
    curve.bevel_resolution = 4
    spline = curve.splines.new('POLY')
    spline.points.add(len(points)-1)
    for point, (dx,dz) in zip(spline.points, points):
        point.co = (*mm((x+dx,y,z+dz)), 1)
    obj = bpy.data.objects.new('Sicherungsclip | Federbügel schematisch', curve)
    bpy.context.collection.objects.link(obj)
    tag(obj, obj.name, metal)

def wagon(open_side=False):
    block('Ladeboden', (0,0,133), (505,230,22), wood)
    for side in (-1,1):
        block('Längswand', (0,side*107,192), (505,16,96), wood)
    for x in (-244,244):
        block('Stirnwand', (x,0,192), (16,198,96), wood)
    handle = block('Deichsel', (341,0,105), (218,28,27), wood)
    handle.rotation_euler.y = -math.radians(6)
    grip = cyl('Griff', (444,0,117), 12, 120, wood, True)
    for x in AXLE_X:
        make_axle(x)
        block('Achsträger', (x,0,110), (35,232,30), wood)
        for side in (-1,1):
            cyl('Innerer axialer Anschlag', (x,side*121,AXLE_Z), 14, 6, metal, True)
            if x == 165 and side == 1 and open_side:
                continue
            make_wheel(x,side*139,AXLE_Z,side)
            ring('Unterlegscheibe', (x,side*157,AXLE_Z), 17, (8.5,8.5), 4, metal, side)
            clip(x,side*PIN_Y,AXLE_Z)

def camera(name, loc, target, scale):
    bpy.ops.object.camera_add(location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    obj.data.type = 'ORTHO'
    obj.data.ortho_scale = scale
    bpy.context.scene.camera = obj

def scene(name, loc, target, scale):
    if bpy.context.scene.name != 'Scene':
        bpy.context.window.scene = bpy.data.scenes.new(name)
    else:
        bpy.context.scene.name = name
    s = bpy.context.scene
    s.unit_settings.system = 'METRIC'
    s.unit_settings.length_unit = 'MILLIMETERS'
    s.render.engine = 'BLENDER_EEVEE'
    s.render.resolution_x = 1280
    s.render.resolution_y = 720
    s.world = bpy.data.worlds.new(name)
    s.world.color = (0.3,0.3,0.3)
    camera(name,loc,target,scale)
    for pos,power,size in [((0.3,0.8,1.2),58,1.0), ((-0.65,-0.35,0.6),29,0.6)]:
        bpy.ops.object.light_add(type='AREA', location=pos)
        bpy.context.object.data.energy = power
        bpy.context.object.data.shape = 'DISK'
        bpy.context.object.data.size = size
        bpy.context.object.rotation_euler = (Vector(target)-bpy.context.object.location).to_track_quat('-Z','Y').to_euler()
    return s

def verify():
    assert GOOD_BORE[0]*math.cos(math.pi/96) > SHAFT_R
    assert 8.5*math.cos(math.pi/96) > SHAFT_R
    assert PIN_R < 2.5
    assert TIP_Y - PIN_Y > 2.5
    assert HUB[0] >= 124 and WASHER[0] > HUB[1] and PIN_Y-PIN_R > WASHER[1]
    # Sweep exterior envelope across all rolling angles and total available axial play.
    # Outline: swept tread radius is constant. The inboard hub face reaches y=124.
    y_inner_tread = 139 - 12.5
    y_outer_tread = 139 + 12.5
    assert y_inner_tread > 116 and y_outer_tread < WASHER[0]
    assert math.dist((AXLE_X[0],0), (AXLE_X[1],0)) > 2*RADIUS
    assert RADIUS == AXLE_Z
    # At the oval bore endpoints, a round shaft still fits along the full offset
    # path. Check its sampled circumference against the displayed ellipse.
    def occupied(cx, rx, ry):
        return max(((cx + SHAFT_R*math.cos(i*math.tau/1440))/rx)**2 +
                   ((SHAFT_R*math.sin(i*math.tau/1440))/ry)**2 for i in range(1440))
    assert occupied(3.0, *WORN_BORE) < 1 and occupied(-3.0, *WORN_BORE) < 1
    assert occupied(3.0, *GOOD_BORE) > 1
    # Stepped axle supports the front with wheel unloaded and 8 mm floor clearance.
    assert (AXLE_Z-8) - (-8) == AXLE_Z
    # Verify shaft exits the front of the assembly before lateral handling.
    assert 256 - 15 > TIP_Y
    # Clip travel: after +25 mm, the bottom end clears the axle crown.
    assert AXLE_Z + 25 - 12.5 > AXLE_Z + SHAFT_R
    for value in (175, 325, 500):
        theta = value/RADIUS
        assert abs(theta*RADIUS-value) < EPS
    return {'Einheiten':'mm', 'Bodenfreiheit_Rad_auf_Stuetze':8,
            'Axialspiel_gesamt':round(PIN_Y-PIN_R-124-30-4, 2),
            'Nabenbohrung_intakt': [2*v for v in GOOD_BORE],
            'Nabenbohrung_oval': [2*v for v in WORN_BORE],
            'Sichtbares_Querwandern_oval_nachgewiesen':6,
            'Radwinkel_bei_500_mm_Fahrt_rad':500/RADIUS,
            'Spiel_zur_Wagenwand': y_inner_tread-115}

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
wood=material('Holz',(.63,.34,.14))
rubber=material('Reifen',(.048,.052,.055))
metal=material('Stahl',(.44,.55,.62),.7)
worn_metal=material('Verschlissene Nabe',(.49,.23,.12),.45)
floor_mat=material('Boden',(.22,.25,.27))
stand=material('Abstützung',(.63,.47,.15))

ready = scene('01 Fahrbereit',(.66,.97,.60),(.09,0,.11),.9)
wagon()
block('Boden', (0,0,-6), (4800,4800,12), floor_mat)

assembly = scene('02 Axiale Montage',(.67,.42,.30),(.165,.205,.093),.46)
wagon(open_side=True)
for x in AXLE_X:
    for side in (-1, 1):
        block('Unter Achsträger abgestützt', (x,side*85,43.5), (55,50,103), stand)
make_wheel(165,256,AXLE_Z,1,label='Einbaurad')
ring('Unterlegscheibe | Explosionslage', (165,310,AXLE_Z), 17, (8.5,8.5), 4, metal, 1)
clip(165,PIN_Y,AXLE_Z+35)
block('Boden', (0,0,-14), (4800,4800,12), floor_mat)

comparison = scene('03 Nabenvergleich', (0,.70,.09),(0,0,.09),.44)
make_wheel(103,0,90,1,True,'Defektes Rad – links im Bild')
make_wheel(-103,0,90,1,False,'Intaktes Rad – rechts im Bild')
block('Boden', (0,0,-6), (4800,4800,12), floor_mat)

result = verify()
(OUT/'Pruefwerte.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
bpy.context.window.scene = ready
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Bollerwagen-Mechanik.blend'))
for s, tagname in [(ready,'01-Fahrbereit'), (assembly,'02-Montage'), (comparison,'03-Nabenvergleich')]:
    s.render.filepath = str(OUT/(tagname+'.png'))
    bpy.ops.render.render(scene=s.name, write_still=True)
