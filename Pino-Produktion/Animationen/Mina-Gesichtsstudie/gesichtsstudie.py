"""Blender --factory-startup -b Mina-Rig-und-Bewegungen.blend -P gesichtsstudie.py"""
from pathlib import Path
import os, math, bpy, sys
from mathutils import Vector, Matrix, Quaternion, Euler
from mathutils.bvhtree import BVHTree
from math import sin, cos, pi, sqrt
out = Path(__file__).resolve().parent
scene=bpy.context.scene
rig=next(o for o in scene.objects if o.type=='ARMATURE')
mesh=next(o for o in scene.objects if o.type=='MESH')
anchor=next(o for o in scene.objects if o.type=='EMPTY')
rig.animation_data_clear()
for bone in rig.pose.bones:
    bone.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update()
# Lower the arms into a natural, relaxed portrait pose in world space.
def rotate_rest(name, axis, degrees):
    b=rig.pose.bones['mixamorig:'+name]
    basis=(rig.matrix_world @ b.bone.matrix_local).to_quaternion()
    b.rotation_mode='QUATERNION'
    b.rotation_quaternion=Quaternion(basis.inverted() @ Vector(axis), math.radians(degrees))
for name,sign in [('Left',1),('Right',-1)]:
    rotate_rest(name+'Arm',(0,1,0),sign*72)
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
ev=mesh.evaluated_get(deps)
poly=ev.to_mesh()
tree=BVHTree.FromPolygons([ev.matrix_world@v.co for v in poly.vertices],
                          [p.vertices[:] for p in poly.polygons])
ev.to_mesh_clear()
scene.render.engine='BLENDER_EEVEE'
scene.eevee.taa_render_samples=48
scene.render.resolution_x=680
scene.render.resolution_y=680
scene.render.resolution_percentage=100
scene.render.fps=24
scene.frame_start=1
scene.frame_end=240
scene.view_settings.view_transform='Khronos PBR Neutral'
scene.view_settings.exposure=0
mesh.data.materials[0].node_tree.nodes['Normal Map'].inputs['Strength'].default_value=.25
scene.world=bpy.data.worlds.new('Atelier · Licht')
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.72,.67,.59,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.45*2**(-.85)
def aim(obj,target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def portrait(name,x,y):
    bpy.ops.object.camera_add(location=(x,y,1.025))
    obj=bpy.context.object
    obj.name=name
    obj.data.type='ORTHO'
    obj.data.ortho_scale=.517
    aim(obj,(.001,-.035,1.025))
    return obj
front=portrait('Porträt · Frontal',0,-2.5)
side_camera=portrait('Kontrolle · Dreiviertel',1.35,-2.3)
scene.camera=front
def softbox(name,xyz,energy,size,color):
    bpy.ops.object.light_add(type='AREA',location=xyz)
    ob=bpy.context.object
    ob.name=name
    ob.data.energy=energy*2**(-.85)
    ob.data.shape='DISK'
    ob.data.size=size
    ob.data.color=color
    aim(ob,(0,0,1.02))
softbox('Fenster · links',(-.85,-1.1,2),57,.90,(1,.945,.89))
softbox('Aufhellung · rechts',(.85,-1.05,1.35),19,.85,(.82,.90,1))
softbox('Kontur · Haar',(.35,.85,1.9),85,.65,(1,.80,.58))
# Emissive warm paper backdrop, constant through both camera angles.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,1.8,1.0),rotation=(pi/2,0,0))
back=bpy.context.object
back.name='Hintergrund · Papier'
mat=bpy.data.materials.new('Papier · warmes Elfenbein')
mat.use_nodes=True
nodes=mat.node_tree.nodes
emit=nodes.new('ShaderNodeEmission')
emit.inputs[0].default_value=(.99,.916,.793,1)
emit.inputs[1].default_value=3.2*2**(-.85)
mat.node_tree.links.new(emit.outputs[0],nodes['Material Output'].inputs[0])
back.data.materials.append(mat)
def render_still(path):
    scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
if '--probe' in sys.argv:
    scene.render.resolution_percentage=85
    render_still(Path(os.environ['TEMP'])/'mina-neutral-probe.png')
    sys.exit(0)
# Facial drawing plane is calibrated to a 578 px rest-pose portrait.
# Sample the deforming character's rest surface, then parent the result to the head.
from functools import lru_cache
@lru_cache(maxsize=200000)
def surface(x,y):
    wx=(x-289)*.495/578+.001
    wz=1.025+(289-y)*.495/578
    hit,normal,_,_=tree.ray_cast(Vector((wx,-2,wz)),Vector((0,1,0)),3)
    if hit is None:
        raise ValueError(f'Gesicht außerhalb des Netzes: {x}, {y}')
    return wx,hit.y,wz
gp=bpy.data.grease_pencils.new('Mina · Gesichtszeichnungen')
ink=bpy.data.objects.new('Mina · Gesicht | Grease Pencil',gp)
scene.collection.objects.link(ink)
ink.parent=anchor
ink.matrix_parent_inverse=anchor.matrix_world.inverted()
if hasattr(gp,'stroke_depth_order'):
    gp.stroke_depth_order='2D'
def pigment(name,rgb):
    m=bpy.data.materials.new(name)
    bpy.data.materials.create_gpencil_data(m)
    m.grease_pencil.color=(*rgb,1)
    gp.materials.append(m)
    return len(gp.materials)-1
line=pigment('Feder · warmes Sepia',(.036,.012,.005))
lip=pigment('Lippen · Siena',(.17,.045,.011))
brow=pigment('Brauen · Kastanie',(.056,.020,.007))
browhi=pigment('Brauen · Kastanienlicht',(.104,.037,.013))
sclera=pigment('Augen · Porzellan',(.98,.91,.79))
irisrim=pigment('Iris · dunkler Rand',(.048,.019,.008))
iris=pigment('Iris · Bernsteinbraun',(.14,.054,.016))
honey=pigment('Iris · Honig',(.27,.124,.038))
pupil=pigment('Pupille · Espresso',(.014,.006,.003))
glint=pigment('Augen · Lichtreflex',(1.35,1.31,1.21))
freck=pigment('Sommersprossen · Zimt',(.36,.126,.044))
throat=pigment('Mund · Innenraum',(.071,.014,.010))
tongue=pigment('Mund · Zungenlicht',(.53,.119,.080))
teeth=pigment('Mund · Elfenbein',(.99,.89,.74))
water=pigment('Träne · Schattensaum',(.22,.50,.58))
waterlit=pigment('Träne · Licht',(.76,1.10,1.18))
layers={}
for label in ['Sommersprossen','Nase','Augen · Weiß und Iris','Augen · Lider und Wimpern','Augenbrauen','Mund','Tränen']:
    lay=gp.layers.new(label,set_active=True)
    lay.use_lights=False
    layers[label]=lay
def stroke(points,material,radii,depth=.0011):
    return points,material,radii,depth
def curve(fn,n=27):
    return [fn(i/(n-1)) for i in range(n)]
def ellipse(cx,cy,rx,ry):
    return curve(lambda t:(cx+rx*cos(2*pi*t),cy+ry*sin(2*pi*t)),49)
def dot(x,y,r,mat,depth=.0012):
    return stroke([(x,y),(x+.015,y+.015)],mat,r,depth)
def draw(layer,frame,strokes):
    d=layers[layer].frames.new(frame).drawing
    if not strokes: return
    d.add_strokes([len(s[0]) for s in strokes])
    from array import array
    positions, radiuses, indices = array('f'), array('f'), array('i')
    for pts,mi,radii,depth in strokes:
        indices.append(mi)
        for i,(x,y) in enumerate(pts):
            wx,wy,wz=surface(round(x,3),round(y,3))
            positions.extend((wx,wy-depth,wz))
            radiuses.append((radii(i/(len(pts)-1)) if callable(radii) else radii)*.495/578)
    for name,kind,domain,field,values in [
        ('position','FLOAT_VECTOR','POINT','vector',positions),
        ('radius','FLOAT','POINT','value',radiuses),
        ('opacity','FLOAT','POINT','value',array('f',[1])*len(radiuses)),
        ('material_index','INT','CURVE','value',indices)]:
        attr=d.attributes.get(name)
        if attr is None: attr=d.attributes.new(name,kind,domain)
        attr.data.foreach_set(field,values)
    d.tag_positions_changed()
def area(poly,mat,depth=.0015,spacing=1.65):
    """Clipped ink hatching follows the curved skin even in a three-quarter portrait."""
    strokes=[]
    y0=min(y for x,y in poly)
    y1=max(y for x,y in poly)
    count=max(1,math.ceil((y1-y0)/spacing))
    step=(y1-y0)/count
    for i in range(count):
        y=y0+step*(i+.5)
        intersections=[]
        for (x1,a),(x2,b) in zip(poly,poly[1:]+poly[:1]):
            if min(a,b)<=y<max(a,b):
                intersections.append(x1+(x2-x1)*(y-a)/(b-a))
        intersections.sort()
        for left,right in zip(intersections[::2],intersections[1::2]):
            if right<=left: continue
            radius=min(step*.79,max(.18,(right-left)/2))
            x1=left+radius*.65
            x2=max(x1+.01,right-radius*.65)
            strokes.append(stroke(curve(lambda t:(x1+(x2-x1)*t,y),max(2,math.ceil((x2-x1)/6)+1)),mat,radius,depth))
    return strokes
def ease(t):
    t=min(1,max(0,t))
    return t*t*(3-2*t)
def sample(keys,f):
    if f<=keys[0][0]: return keys[0][1]
    for (a,v),(b,w) in zip(keys,keys[1:]):
        if f<=b:return v+(w-v)*ease((f-a)/(b-a))
    return keys[-1][1]
# x, y, radius in the drawing-plane pixel coordinates above.
specks=[]
for side in (-1,1):
    for ax,ay,r in [(44,332,.92),(53,339,1.25),(66,332,1.38),(77,326,.92),(69,345,1.1),(58,349,.91),(84,335,.75)]:
        specks.append(dot(289+side*ax+(.4 if side==1 else 0),ay+(1.8 if side==1 else 0),r,freck))
draw('Sommersprossen',1,specks)
draw('Nase',1,[stroke(curve(lambda t:(278+22*t,332-7.4*sin(pi*t)**.82)),lip,lambda t:1.55+.72*sin(pi*t))])
# Each beat uses a different rhythm, with a breath, held key pose and settling time.
timings=[
 [(1,0),(5,0),(9,-.15),(17,.78),(22,1),(33,.94),(40,.40),(46,0)],
 [(1,0),(4,0),(9,-.24),(16,.85),(20,1),(25,.66),(30,1),(34,.85),(40,.42),(47,0)],
 [(1,0),(7,0),(11,-.18),(15,1),(22,1),(29,.80),(35,.67),(42,.25),(47,0)],
 [(1,0),(5,0),(10,.13),(17,.52),(24,.80),(30,1),(35,.96),(40,.73),(45,.15),(48,0)],
 [(1,0),(6,0),(12,.25),(21,.78),(27,1),(35,1),(41,.59),(47,0)]]
def pose(m,f):
    a=sample(timings[m],f)
    # An early blink anticipates surprise, a single squeezed blink breaks the sad hold.
    blink=sample([(1,0),(7,0),(9,.85),(11,1),(14,0)],f) if m==2 else 0
    if m==3: blink=sample([(1,0),(24,0),(27,.90),(29,.18),(31,0)],f)
    return a,blink
def eyes(m,a,blink):
    whites,lids,brows=[],[],[]
    for side in (-1,1):
        cx=289+side*52.8
        cy=284.2
        rx=31.0
        opening=1.
        tilt=0
        gaze=0
        gaze_y=1.
        by=230
        browtilt=0
        if m==0:
            opening-=.24*a
            cy-=1.5*a
            by-=6*a
            gaze_y-=1.8*a
        elif m==1:
            opening-=1.34*a
            cy+=3.5*a
            by-=6*a
        elif m==2:
            opening+=.18*a
            by-=(10.5 if side==1 else 6.5)*a
            browtilt=7.4*a
            gaze_y-=1.5*a
        elif m==3:
            opening-=.35*a
            tilt=5*a
            by+=3*a
            browtilt=14*a
            gaze_y+=5.2*a
            gaze-=3*a
        elif m==4:
            opening-=(.52 if side==-1 else .1)*a
            by+=(9.5 if side==-1 else -8)*a
            browtilt=(-7 if side==-1 else 6)*a
            gaze+=7.5*a
            gaze_y-=3.6*a
        opening=max(.005,opening*(1-blink))
        rt=28*opening
        rb=27*opening
        def ext(t,top):
            u=-1+2*t
            return cx+rx*u,cy+side*tilt*u+(-rt if top else rb)*sqrt(max(0,1-u*u)) + (1-opening)*(-7)*(1-u*u)
        upper=curve(lambda t:ext(t,True),43)
        lower=curve(lambda t:ext(t,False),43)
        if opening>.07:
            whites.extend(area(upper+lower[::-1],sclera,.0017))
            gx=cx-side*3.5+gaze
            gy=cy+gaze_y
            # Lower and upper lids clip every pigment including specular reflections.
            def clipped_circle(x,y,r,material,depth):
                n=max(3,math.ceil(r*2/1.50))
                result=[]
                for i in range(n):
                    yy=y-r+(i+.5)*(2*r/n)
                    horizontal=r*sqrt(max(0,1-((yy-y)/r)**2))
                    intervals=[]
                    for edge in (upper,lower):
                        for p,q in zip(edge,edge[1:]):
                            if min(p[1],q[1])<=yy<max(p[1],q[1]):
                                intervals.append(p[0]+(q[0]-p[0])*(yy-p[1])/(q[1]-p[1]))
                    if len(intervals)<2: continue
                    lo=max(x-horizontal,min(intervals)+.4)
                    hi=min(x+horizontal,max(intervals)-.4)
                    if hi-lo<.6: continue
                    result.append(stroke(curve(lambda t:(lo+(hi-lo)*t,yy),max(2,math.ceil((hi-lo)/5)+1)),material,min(1.15,(hi-lo)*.5),depth))
                return result
            for ox,oy,r,mat,dp in [(0,0,17.5,irisrim,.0022),(0,.5,15.7,iris,.0025),(0,2,12.7,honey,.0028),(0,-.7,10.9,pupil,.0030),(5.4,-6.2,3.9,glint,.0033),(-5.2,6.1,1.25,glint,.0033)]:
                whites+=clipped_circle(gx+ox,gy+oy,r,mat,dp)
            lids.append(stroke(lower,line,lambda t:.48+.36*sin(pi*t),.00365))
        lids.append(stroke(upper,line,lambda t:.86+(1.65 if opening>.2 else 2.1)*sin(pi*t)**.6,.00375))
        if opening>.2:
            for u,le in [(.88,3.35),(.965,2.75)]:
                t=(1+side*u)/2
                x,y=ext(t,True)
                lids.append(stroke(curve(lambda q:(x+side*(le*q+q*q*.8),y-le*q*(1.3-.35*q)),8),line,lambda q:1.13*(1-q)+.28,.00382))
        # Inner brow is full and blunt, outer tail tapers into a fine point.
        def spine(t):
            return cx+side*(-25+55*t),by-8.6*sin(pi*(.10+.85*t))+6.4*t + browtilt*(2*t-1)
        def thick(t):
            return (1+4.3*(1-t)**.6+2.7*sin(pi*t)**.8)*(.22+.78*min(1,t/.06)**.38)
        contour=[(x,y-thick(t)*.64) for t in [i/34 for i in range(35)] for x,y in [spine(t)]]
        contour += [(x,y+thick(t)*.66) for t in [1-i/34 for i in range(35)] for x,y in [spine(t)]]
        brows+=area(contour,brow,.00155,1.05)
        for u in (.13,.25,.41):
            x,y=spine(u)
            brows.append(stroke(curve(lambda t:(x+side*4*t,y+2-4.5*t),7),browhi,lambda t:.26+.28*sin(pi*t),.00195))
    return whites,lids,brows
def lips(m,a):
    cx,cy,rx=289,369,18
    curve_y=1.0
    gape=0
    slant=0
    if m==0: rx+=9*a;cy-=1*a;curve_y+=10*a
    if m==1: rx+=8.2*a;cy-=2.5*a;curve_y+=5*a;gape=25*a
    if m==2: rx-=10.7*a;cy+=2*a;curve_y-=1*a;gape=17*a
    if m==3: rx-=1.5*a;cy+=3*a;curve_y-=9*a;slant=-1*a;gape=2*a
    if m==4: rx-=3*a;cx+=8*a;curve_y-=1.3*a;slant=-3.0*a
    def shape(t,bottom=0):
        u=2*t-1
        v=max(0,1-u*u)
        return cx+rx*u,cy+slant*u+curve_y*v+gape*(.71 if bottom else -.29)*sqrt(v)
    upper=curve(lambda t:shape(t),39)
    if gape<2.2:
        return [stroke(upper,lip,lambda t:.63+1.44*sin(pi*t)**.5,.00155)]
    lower=curve(lambda t:shape(t,1),39)
    form=upper+lower[::-1]
    inside=area(form,throat,.00155,1.05)
    if m==1 and gape>8:
        top=curve(lambda t:shape(.085+.83*t),27)
        teethline=[(x,y+gape*.18*max(0,sin(pi*i/(len(top)-1)))**.45) for i,(x,y) in enumerate(top)]
        inside+=area(top+teethline[::-1],teeth,.0019,1.0)
        base=curve(lambda t:shape(.20+.62*t,1),27)
        tip=[(x,y-gape*.23*max(0,sin(pi*i/(len(base)-1)))**.6) for i,(x,y) in enumerate(base)]
        inside+=area(base+tip[::-1],tongue,.00195,1.)
    inside+=[stroke(upper,lip,lambda t:.63+1.12*sin(pi*t)**.5,.0022),stroke(lower,lip,lambda t:.62+.76*sin(pi*t)**.5,.0022)]
    return inside
def tears(f):
    result=[]
    for side,delay in [(-1,0),(1,5)]:
        age=sample([(1,0),(17+delay,0),(23+delay,.21),(33+delay,.70),(40+delay,1),(48,1)],f)
        fade=sample([(1,1),(40+delay,1),(47,0)],f)
        if age<.02 or fade<.05: continue
        lid_y=300.5
        path_length=53 if side==-1 else 36
        def track(t):
            return 289+side*(64+4*sin(pi*t*.78)),lid_y+path_length*t
        x,y=track(age)
        size=(3.4+2.5*age)*(1 if side==-1 else .83)*min(1,age*6)*fade
        if age>.08:
            trail=curve(lambda u:track(u*age),20)
            result.append(stroke(trail,water,lambda u:(.21+1.0*u**1.8)*fade,.00205))
            result.append(stroke([(xx-.43,yy) for xx,yy in trail],waterlit,lambda u:(.22+.37*u)*fade,.00215))
        def drop(t):
            ang=2*pi*t
            return x+size*sin(ang)*(.74-.30*cos(ang)),y-size*(1.35*cos(ang)+.18*cos(2*ang))
        contour=curve(drop,31)
        result+=area(contour,water,.002, .76)
        result.append(stroke(curve(lambda t:(x-size*.26-size*.12*sin(pi*t),y-size*.25+size*.73*t),8),waterlit,.56*fade,.0022))
    return result
for idx,title in enumerate(['Freude','Lachen','Verwunderung','Trauer und Weinen','Skepsis und Grübeln']):
    offset=idx*48
    scene.timeline_markers.new(title,frame=offset+1)
    previous=None
    for f in sorted(set(range(1,49,2))|{48}):
        a,blink=pose(idx,f)
        state=(round(a,4),round(blink,4))
        if previous==state and idx!=3: continue
        previous=state
        whites,lids,brows=eyes(idx,a,blink)
        draw('Augen · Weiß und Iris',offset+f,whites)
        draw('Augen · Lider und Wimpern',offset+f,lids)
        draw('Augenbrauen',offset+f,brows)
        draw('Mund',offset+f,lips(idx,a))
        if idx==3 or f==1: draw('Tränen',offset+f,tears(f) if idx==3 else [])
    # Degrees in portrait/world X (nod), Z (turn), Y (tilt). Neck carries a portion of the acting.
    turns=[(-2.5,2.4,-4.8),(-6.3,-3.2,4.3),(-7.6,3.8,-2.8),(7.4,-4.1,3.8),(2.0,9,-5.8)]
    for f in sorted(set([1,48]+[k for k,v in timings[idx]])):
        a=pose(idx,f)[0]
        for name,share in [('Neck',.31),('Head',.69)]:
            b=rig.pose.bones['mixamorig:'+name]
            basis=(rig.matrix_world@b.bone.matrix_local).to_quaternion()
            pitch,yaw,roll=turns[idx]
            world=Euler(tuple(math.radians(value*a*share) for value in (pitch,roll,yaw)),'XYZ').to_quaternion()
            b.rotation_mode='QUATERNION'
            b.rotation_quaternion=basis.inverted()@world@basis
            b.keyframe_insert(data_path='rotation_quaternion',frame=offset+f,group=name)
rig.animation_data.action.name='Mina · fünf emotionale Porträtstudien'
scene.frame_set(1)
gp.layers.active=layers['Augenbrauen']
bpy.ops.object.select_all(action='DESELECT')
ink.select_set(True)
bpy.context.view_layer.objects.active=ink
for screen in bpy.data.screens:
    for ar in screen.areas:
        if ar.type=='VIEW_3D':
            ar.spaces.active.region_3d.view_perspective='CAMERA'
            ar.spaces.active.overlay.show_overlays=False
            ar.spaces.active.shading.type='MATERIAL'
bpy.context.preferences.filepaths.save_version=0
scene.render.filepath='//Mina-'
scene.render.image_settings.file_format='PNG'
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Mina-Gesichtsstudie.blend'),compress=True)
for frame,label in [(1,'Neutral'),(22,'Freude'),(67,'Lachen'),(113,'Verwunderung'),(177,'Weinen'),(221,'Skepsis')]:
    scene.frame_set(frame)
    render_still(out/f'{frame:03d}-{label}.png')
scene.camera=side_camera
scene.frame_set(113)
render_still(out/'113-Verwunderung-Dreiviertel.png')
