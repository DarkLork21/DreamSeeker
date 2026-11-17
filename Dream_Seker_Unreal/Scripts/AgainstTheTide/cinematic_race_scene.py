"""A longer, vaulted sunset pool with continuous water and restrained detail batches."""
import unreal,math,random
from pathlib import Path
random.seed(113)
A=unreal.EditorAssetLibrary;E=unreal.MaterialEditingLibrary;L=unreal.BlueprintEditorLibrary
ROOT='/Game/DreamSeeker/Levels/AgainstTheTide';ART=ROOT+'/Cinematic';END=15000
tools=unreal.AssetToolsHelpers.get_asset_tools();levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
source=Path(__file__).parent/'race-art-source';source.mkdir(exist_ok=True)
def mat(name,rgb,unlit=False,opacity=None,rough=.6,grain=False):
    path=ART+'/Materials/'+name;m=A.load_asset(path) if A.does_asset_exist(path) else tools.create_asset(name,ART+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
    E.delete_all_material_expressions(m);m.set_editor_property('two_sided',True)
    def n(kind,x,y):return E.create_material_expression(m,kind,x,y)
    c=n(unreal.MaterialExpressionConstant3Vector,-500,0);c.set_editor_property('constant',unreal.LinearColor(*rgb,1));out=c
    if grain:
        noise=n(unreal.MaterialExpressionNoise,-700,250);noise.set_editor_property('scale',.04);noise.set_editor_property('levels',2);noise.set_editor_property('output_min',.82);noise.set_editor_property('output_max',1.05)
        out=n(unreal.MaterialExpressionMultiply,-200,0);E.connect_material_expressions(c,'',out,'A');E.connect_material_expressions(noise,'',out,'B')
    m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT if unlit else unreal.MaterialShadingModel.MSM_DEFAULT_LIT)
    E.connect_material_property(out,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR if unlit else unreal.MaterialProperty.MP_BASE_COLOR)
    r=n(unreal.MaterialExpressionConstant,-200,200);r.set_editor_property('r',rough);E.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS)
    if opacity is not None:
        m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT);o=n(unreal.MaterialExpressionConstant,-200,350);o.set_editor_property('r',opacity);E.connect_material_property(o,'',unreal.MaterialProperty.MP_OPACITY)
    E.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES);E.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_NANITE);E.recompile_material(m);assert A.save_loaded_asset(m,False);return m
stone=mat('M_WeatheredLimestone',(.26,.23,.19),grain=True);dark=mat('M_DeepSlate',(.025,.045,.065),grain=True);brass=mat('M_AntiqueBrass',(.23,.15,.065),rough=.35)
plaster=mat('M_DuskPlaster',(.13,.16,.18),grain=True);tile=mat('M_GlazedPoolTile',(.055,.14,.16),rough=.24);grout=mat('M_TileGrout',(.09,.15,.16))
glass=mat('M_QuietWindowGlass',(.18,.18,.24),True,.12);warm=mat('M_LanternCore',(.55,.27,.09),True);ivory=mat('M_LaneIvory',(.48,.45,.35));coral=mat('M_LaneCoral',(.38,.10,.07));leaves=mat('M_Ivy',(.035,.065,.04));spectator=mat('M_CrowdShadow',(.035,.028,.05));coat=mat('M_CrowdCoat',(.075,.055,.07))
water=mat('M_DeepWaterVeil',(.018,.095,.13),True,.18);surface=mat('M_LivingWaterSurface',(.028,.13,.16),False,.34,.12);raymat=mat('M_SunsetHaze',(.7,.35,.15),True,.035)
# Slow world-space ripples deform the surface by only a few centimetres.
m=surface
def n(kind,x,y):return E.create_material_expression(m,kind,x,y)
def connect(a,b,p):
    names=E.get_material_expression_input_names(b)
    if p=='Input' and p not in names:p=names[0]
    assert E.connect_material_expressions(a,'',b,p)
def const(v,x,y):
    o=n(unreal.MaterialExpressionConstant,x,y);o.set_editor_property('r',v);return o
pos=n(unreal.MaterialExpressionWorldPosition,-1300,650);mask=n(unreal.MaterialExpressionComponentMask,-1100,650);mask.set_editor_property('r',True);connect(pos,mask,'Input')
scale=n(unreal.MaterialExpressionMultiply,-900,650);connect(mask,scale,'A');connect(const(.003,-1100,800),scale,'B')
time=n(unreal.MaterialExpressionTime,-1100,950);rate=n(unreal.MaterialExpressionMultiply,-900,950);connect(time,rate,'A');connect(const(.13,-1100,1100),rate,'B')
phase=n(unreal.MaterialExpressionAdd,-700,650);connect(scale,phase,'A');connect(rate,phase,'B');sine=n(unreal.MaterialExpressionSine,-500,650);connect(phase,sine,'Input')
amp=n(unreal.MaterialExpressionMultiply,-300,650);connect(sine,amp,'A');connect(const(2.4,-500,820),amp,'B')
offset=n(unreal.MaterialExpressionAppendVector,-100,650);zero=n(unreal.MaterialExpressionConstant2Vector,-350,1020);connect(zero,offset,'A');connect(amp,offset,'B');assert E.connect_material_property(offset,'',unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
# A quiet scrolling noise normal breaks up the large water highlights.
noise=n(unreal.MaterialExpressionNoise,-800,1350);noise.set_editor_property('scale',.018);noise.set_editor_property('levels',2);noise.set_editor_property('output_min',-.10);noise.set_editor_property('output_max',.10)
xy=n(unreal.MaterialExpressionAppendVector,-500,1350);connect(noise,xy,'A');connect(sine,xy,'B');normal=n(unreal.MaterialExpressionAppendVector,-250,1350);connect(xy,normal,'A');connect(const(1,-500,1520),normal,'B');assert E.connect_material_property(normal,'',unreal.MaterialProperty.MP_NORMAL)
E.recompile_material(m);assert A.save_loaded_asset(m,False)
def mesh(name,v,f):
    path=ART+'/Meshes/'+name
    if A.does_asset_exist(path):return A.load_asset(path)
    lines=['o '+name,'s 1']+[f'v {x:.3f} {-y:.3f} {z:.3f}' for x,y,z in v]+[f'vt {x/600:.5f} {y/600:.5f}' for x,y,z in v]+['f '+' '.join(f'{i+1}/{i+1}' for i in face) for face in f]
    filename=source/(name+'.obj');filename.write_text('\n'.join(lines));task=unreal.AssetImportTask()
    for k,value in {'filename':str(filename),'destination_path':ART+'/Meshes','destination_name':name,'automated':True,'save':True}.items():task.set_editor_property(k,value)
    tools.import_asset_tasks([task]);result=A.load_asset(path);assert result,name;return result
def grid(name,nx,ny,fun):
    v=[fun(i/nx,j/ny) for i in range(nx+1) for j in range(ny+1)];f=[]
    for i in range(nx):
        for j in range(ny):
            a=i*(ny+1)+j;b=a+ny+1;f.extend(((a,b,b+1),(a,b+1,a+1)))
    return mesh(name,v,f)
wave=grid('SM_LongPoolSurface',160,12,lambda u,v:(-300+16300*u,-1300+1680*v,0))
vault=grid('SM_BarrelVault',1,36,lambda u,v:(-500+17000*u,-650+1650*math.cos(v*math.pi),1400+900*math.sin(v*math.pi)))
# Extruded stone arch ring, including both jambs, with smooth segmented curves.
v=[];f=[]
for depth in (-45,45):
    for radius in (340,385):
        for j in range(25):
            t=j*math.pi/24;v.append((math.cos(t)*radius,depth,580+math.sin(t)*radius))
for j in range(24):
    f.extend(((j,j+1,25+j+1,25+j),(50+j,75+j,75+j+1,50+j+1),(j,50+j,50+j+1,j+1),(25+j,25+j+1,75+j+1,75+j)))
arch=mesh('SM_WindowArch',v,f)
window=mesh('SM_ArchedGlass',[(0,0,440),(-340,0,0),(340,0,0)]+[(340*math.cos(j*math.pi/24),0,580+340*math.sin(j*math.pi/24)) for j in range(25)],[(0,i,i+1) for i in range(1,27)]+[(0,27,1)])
flag=mesh('SM_RacePennant',[(0,0,0),(0,70,0),(0,35,-80)],[(0,1,2)])
shaft=mesh('SM_DreamSunbeam',[(0,0,0),(210,0,0),(950,0,-950),(350,0,-950)],[(0,1,2),(0,2,3)])
assert levels.load_level(ROOT+'/LV_AgainstTheTide')
for a in list(actors.get_all_level_actors()):
    if isinstance(a,(unreal.StaticMeshActor,unreal.TextRenderActor,unreal.DirectionalLight,unreal.SkyLight,unreal.PointLight,unreal.ExponentialHeightFog,unreal.PostProcessVolume)) or a.get_class().get_name()=='BP_MemoryDetails_C':actors.destroy_actor(a)
cube=A.load_asset('/Engine/BasicShapes/Cube');sphere=A.load_asset('/Engine/BasicShapes/Sphere');cyl=A.load_asset('/Engine/BasicShapes/Cylinder');batchclass=A.load_blueprint_class('/Game/DreamSeeker/DreamHub/MemoryCauseway/BP_MemoryDetails');batches={}
def spawn(cls,name,xyz=(0,0,0),rot=(0,0,0)):
    a=actors.spawn_actor_from_class(cls,unreal.Vector(*xyz),unreal.Rotator(*rot));a.set_actor_label(name);a.set_folder_path(unreal.Name('Against the Tide / Cinematic'));return a
def actor(mesh,name,xyz,scale,mat,solid=False):
    a=spawn(unreal.StaticMeshActor,name,xyz);c=a.static_mesh_component;c.set_static_mesh(mesh);c.set_material(0,mat);c.set_collision_profile_name('BlockAll' if solid else 'NoCollision');a.set_actor_scale3d(unreal.Vector(*scale));return a
def instance(mesh,mat,xyz,scale=(1,1,1),rot=(0,0,0)):
    key=(mesh.get_path_name(),mat.get_path_name())
    if key not in batches:
        a=spawn(batchclass,'Cinematic detail batch '+str(len(batches)));c=a.get_component_by_class(unreal.InstancedStaticMeshComponent);c.set_static_mesh(mesh);c.set_material(0,mat);c.set_collision_profile_name('NoCollision');batches[key]=c
    batches[key].add_instance(unreal.Transform(location=unreal.Vector(*xyz),rotation=unreal.Rotator(*rot),scale=unreal.Vector(*scale)),True)
def beam(a,b,width,mat):
    p=unreal.Vector(*a);q=unreal.Vector(*b);d=q-p;r=unreal.MathLibrary.find_look_at_rotation(p,q);instance(cube,mat,((p.x+q.x)/2,(p.y+q.y)/2,(p.z+q.z)/2),(d.length()/100,width/100,width/100),(r.roll,r.pitch,r.yaw))
def text(label,xyz,size=42):
    a=spawn(unreal.TextRenderActor,label,xyz,(0,0,90));c=a.text_render;c.set_text(label);c.set_world_size(size);c.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER);c.set_text_render_color(unreal.Color(236,213,168));return a
actor(cube,'Solid tiled pool bed',(7700,-500,-460),(167,18,1),tile,True)
actor(cube,'Dark pool foundation',(7700,-500,-825),(167,20,6.8),dark)
actor(cube,'Rear pool wall',(7700,-1320,-205),(167,.7,5),tile,True)
actor(cube,'Gallery deck',(7700,-1670,15),(167,6.5,.9),stone)
actor(cube,'Starting terrace',(-300,-500,35),(9,18,1.2),stone)
actor(cube,'Finish terrace',(15550,-500,35),(9,18,1.2),stone)
actor(cube,'Water depth',(7700,-500,-210),(167,16.5,4.1),water)
actor(wave,'Continuous moving pool surface',(0,0,0),(1,1,1),surface)
actor(vault,'Dark barrel-vault ceiling',(0,0,0),(1,1,1),dark)
actor(cube,'Gallery lower wall',(7700,-2080,180),(167,1.5,5.4),plaster)
actor(cube,'Wall below pool water',(7700,-1240,-200),(167,.16,4),tile)
actor(cube,'Continuous gallery cornice',(7700,-2080,1460),(167,2.2,.6),stone)
for x in range(-500,16000,90):
    beam((x,-1280,-400),(x,380,-400),1.4,grout)
for y in range(-1260,401,90):beam((-500,y,-400),(16000,y,-400),1.4,grout)
for y in (150,-150,-450,-750,-1050):
    beam((0,y,4),(15300,y,4),2.2,ivory)
    for j,x in enumerate(range(0,15300,45)):instance(sphere,coral if j%6<3 else ivory,(x,y,5),(.17,.17,.13))
for y in (0,-300,-600,-900):
    beam((150,y,-395),(15000,y,-395),9,dark)
    for x in (4200,8200,12000):beam((x-70,y-80,-392),(x-70,y+80,-392),10,ivory)
    actor(cube,'Starting block',(0,y,150),(1.3,1.7,.35),stone);actor(cube,'Starting pedestal',(-15,y,75),(.65,.8,1.3),dark)
    actor(cube,'Finish timing pad',(15120,y,-105),(.15,2.8,2.3),dark)
    for x in (14500,15000):beam((x,y-120,-390),(x,y+120,-390),18,ivory)
sky=A.duplicate_asset('/Game/DreamSeeker/Levels/FirstRipple/Polish/Materials/M_MemorySky',ART+'/Materials/M_DistantSunset') if not A.does_asset_exist(ART+'/Materials/M_DistantSunset') else A.load_asset(ART+'/Materials/M_DistantSunset')
sky.set_editor_property('two_sided',True);E.recompile_material(sky);assert A.save_loaded_asset(sky,False)
actor(sphere,'Dusk beyond the glass',(7500,-8000,2400),(370,370,370),sky)
actor(sphere,'Low remembered sun',(5000,-9000,900),(9,1.5,9),warm)
for index,x in enumerate(range(-350,16400,850)):
    instance(arch,stone,(x+425,-2020,450));instance(arch,brass,(x+425,-1960,455),(.91,.35,.94));instance(window,glass,(x+425,-2050,450))
    for side in (-1,1):
        xx=x+425+side*362;instance(cube,stone,(xx,-2020,735),(.45,.9,5.8))
    instance(cyl,stone,(x,-2000,865),(1.15,1.15,11.7));instance(cyl,brass,(x,-2000,306),(1.6,1.6,.2));instance(cyl,stone,(x,-2000,1450),(1.6,1.6,.7))
    for dx in (-30,0,30):beam((x+dx,-1938,330),(x+dx,-1938,1400),4,brass)
    beam((x+425,-1950,455),(x+425,-1950,1340),8,brass)
    beam((x+95,-1950,990),(x+755,-1950,990),8,brass)
    instance(cube,dark,(x+425,-1860,245),(8.4,3.5,.35));beam((x,-1690,455),(x+850,-1690,455),8,brass)
    for dx in range(40,840,85):instance(cyl,brass,(x+dx,-1690,353),(.035,.035,2.0))
    for j in range(5 if 5<index<13 else 3):
        xx=x+110+j*140+random.uniform(-25,25);height=random.uniform(105,145)
        instance(sphere,coat if j%2 else spectator,(xx,-1860,285+height*.35),(.45,.32,height/100))
        instance(sphere,spectator,(xx,-1850,300+height),(.34,.34,.38))
        beam((xx-18,-1825,340),(xx-35,-1810,385),10,spectator)
    # Repeated vault ribs and a second fine brass line articulate the roof.
    for j in range(22):
        a=j*math.pi/22;b=(j+1)*math.pi/22
        beam((x,-650+1645*math.cos(a),1400+895*math.sin(a)),(x,-650+1645*math.cos(b),1400+895*math.sin(b)),17,brass)
    instance(sphere,warm,(x,-1885,705),(.23,.23,.42));instance(cube,brass,(x,-1910,705),(.48,.3,.8))
    if index%3==0:
        light=spawn(unreal.PointLight,'Amber gallery pool',(x,-1610,670));c=light.get_component_by_class(unreal.PointLightComponent);c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_intensity(160);c.set_light_color(unreal.LinearColor(1,.53,.25));c.set_attenuation_radius(600);c.set_cast_shadows(False)
        instance(shaft,raymat,(x+250,-1300,1200),(1,1,1))
    if index%4==0:
        for j in range(18):instance(sphere,leaves,(x+random.uniform(-70,70),-1890,1400-j*48),(random.uniform(.16,.36),.06,.18),(0,0,random.uniform(-50,50)))
# The central section is quieter and cooler; the final gallery opens into light.
for x,label in ((1900,'FIND YOUR RHYTHM'),(7600,'KEEP YOUR COMPOSURE'),(13100,'TRUST YOUR STROKE')):text(label,(x,-1940,555),30)
for x in (600,15000):
    beam((x,-1200,255),(x,250,255),3,brass)
    for i,y in enumerate(range(-1140,201,100)):instance(flag,coral if i%2 else ivory,(x,y,255))
text('AGAINST THE TIDE',(950,-1930,1130),42);text('FINISH',(15000,-1660,580),48)
sun=spawn(unreal.DirectionalLight,'Low cinematic sunset',(0,0,2000),(0,-12,50));c=sun.get_component_by_class(unreal.DirectionalLightComponent);c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_intensity(2.0);c.set_light_color(unreal.LinearColor(1,.64,.39));c.set_editor_property('volumetric_scattering_intensity',1.5)
fill=spawn(unreal.SkyLight,'Cool interior fill',(7000,-600,1200));c=fill.get_component_by_class(unreal.SkyLightComponent);c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_editor_property('real_time_capture',True);c.set_intensity(.22)
fog=spawn(unreal.ExponentialHeightFog,'Still air above the pool',(0,0,-100));c=fog.get_component_by_class(unreal.ExponentialHeightFogComponent);c.set_editor_property('fog_density',.0015);c.set_editor_property('fog_height_falloff',.22);c.set_volumetric_fog(True)
post=spawn(unreal.PostProcessVolume,'Cinematic exposure');post.set_editor_property('unbound',True);settings=post.get_editor_property('settings')
for key,val in (('auto_exposure_bias',-.5),('bloom_intensity',.35),('vignette_intensity',.22),('motion_blur_amount',.12)):
    settings.set_editor_property('override_'+key,True);settings.set_editor_property(key,val)
post.set_editor_property('settings',settings)
for a in actors.get_all_level_actors():
    if a.get_class().get_name()=='BP_RaceDirector_C':a.set_editor_property('FinishX',float(END))
    if a.get_class().get_name()=='BP_DreamCompletion_C':a.set_actor_location(unreal.Vector(END,0,0),False,False)
assert levels.save_current_level()
unreal.log('CINEMATIC_RACE_READY actors='+str(len(actors.get_all_level_actors()))+' batches='+str(len(batches)))
