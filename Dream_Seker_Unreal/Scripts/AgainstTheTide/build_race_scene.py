"""A sunset competition pool with native geometry, layered lanes and spectators."""
import unreal,math,random
random.seed(34)
A=unreal.EditorAssetLibrary;L=unreal.BlueprintEditorLibrary;E=unreal.MaterialEditingLibrary
ROOT='/Game/DreamSeeker/Levels/AgainstTheTide';MAP=ROOT+'/LV_AgainstTheTide';HUB='/Game/DreamSeeker/DreamHub/MemoryCauseway'
tools=unreal.AssetToolsHelpers.get_asset_tools();actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
def material(name,rgb,glow=False,alpha=None):
    path=ROOT+'/Materials/'+name
    if A.does_asset_exist(path):return A.load_asset(path)
    m=tools.create_asset(name,ROOT+'/Materials',unreal.Material,unreal.MaterialFactoryNew());m.set_editor_property('two_sided',True)
    c=E.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-300,0);c.set_editor_property('constant',unreal.LinearColor(*rgb,1))
    if glow:m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT)
    E.connect_material_property(c,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR if glow else unreal.MaterialProperty.MP_BASE_COLOR)
    rough=E.create_material_expression(m,unreal.MaterialExpressionConstant,-300,170);rough.set_editor_property('r',.38 if 'Tile' in name else .7);E.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
    if alpha is not None:
        m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT);o=E.create_material_expression(m,unreal.MaterialExpressionConstant,-300,300);o.set_editor_property('r',alpha);E.connect_material_property(o,'',unreal.MaterialProperty.MP_OPACITY)
    E.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES);E.recompile_material(m);assert A.save_loaded_asset(m,False);return m
ivory=material('M_WarmStone',(.38,.31,.23));tile=material('M_TealTile',(.055,.16,.17));gold=material('M_Brass',(.37,.21,.07));deep=material('M_ShadowBlue',(.025,.045,.07));rose=material('M_RoseTile',(.24,.10,.10))
water=material('M_PoolWater',(.035,.20,.24),True,.13);glass=material('M_SunsetGlass',(.75,.33,.17),True,.18);light=material('M_LampGlow',(.8,.5,.22),True);rope=material('M_LaneIvory',(.60,.52,.35))
coral=material('M_CoralCap',(.60,.09,.06));cream=material('M_IvoryCap',(.72,.65,.44));violet=material('M_VioletCap',(.16,.055,.25));silhouette=material('M_SpectatorSilhouette',(.055,.035,.075));leaf=material('M_ClimbingLeaves',(.08,.12,.055))
cube=A.load_asset('/Engine/BasicShapes/Cube');sphere=A.load_asset('/Engine/BasicShapes/Sphere');cylinder=A.load_asset('/Engine/BasicShapes/Cylinder')
world=unreal.EditorLoadingAndSavingUtils.new_blank_map(False);world.get_world_settings().set_editor_property('default_game_mode',A.load_blueprint_class(ROOT+'/BP_RaceMode'))
def spawn(cls,name,xyz):
    a=actors.spawn_actor_from_class(cls,unreal.Vector(*xyz));a.set_actor_label(name);a.set_folder_path(unreal.Name('Against the Tide'));return a
def shape(mesh,name,xyz,scale,mat,solid=False):
    a=spawn(unreal.StaticMeshActor,name,xyz);c=a.static_mesh_component;c.set_static_mesh(mesh);c.set_material(0,mat);c.set_collision_profile_name('BlockAll' if solid else 'NoCollision');a.set_actor_scale3d(unreal.Vector(*scale));return a
def beam(name,start,end,width,mat):
    a=unreal.Vector(*start);b=unreal.Vector(*end);d=b-a;r=unreal.MathLibrary.find_look_at_rotation(a,b);o=shape(cube,name,((a.x+b.x)/2,(a.y+b.y)/2,(a.z+b.z)/2),(d.length()/100,width/100,width/100),mat);o.set_actor_rotation(r,False);return o
def text(name,label,xyz,size=42):
    a=spawn(unreal.TextRenderActor,name,xyz);c=a.text_render;c.set_text(label);c.set_world_size(size);c.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER);c.set_text_render_color(unreal.Color(247,223,177));a.set_actor_rotation(unreal.Rotator(0,0,90),False);return a
# Long clean swim corridor, with front cutaway so steering remains readable.
shape(cube,'Tiled pool floor',(4200,-500,-450),(90,17,1),tile,True)
shape(cube,'Front pool coping',(4200,510,50),(90,2,.55),ivory)
shape(cube,'Rear deck',(4200,-1570,30),(90,8,1.2),ivory)
shape(cube,'Rear pool wall',(4200,-1280,-190),(90,.7,5),tile,True)
shape(cube,'Starting deck',(-210,-500,25),(6,18,1),ivory)
shape(cube,'Finish deck',(8500,-500,25),(7,18,1),ivory)
shape(cube,'Clear teal pool',(4200,-500,-205),(90,16,4.1),water)
# Instanced accents keep the repeated architectural details economical.
batches={}
batchclass=A.load_blueprint_class('/Game/DreamSeeker/DreamHub/MemoryCauseway/BP_MemoryDetails')
def instance(mesh,mat,xyz,scale,rot=(0,0,0)):
    key=(mesh.get_path_name(),mat.get_path_name())
    if key not in batches:
        a=spawn(batchclass,'Pool detail batch '+str(len(batches)),(0,0,0));c=a.get_component_by_class(unreal.InstancedStaticMeshComponent);c.set_static_mesh(mesh);c.set_material(0,mat);c.set_collision_profile_name('NoCollision');batches[key]=c
    c=batches[key];c.add_instance(unreal.Transform(location=unreal.Vector(*xyz),rotation=unreal.Rotator(*rot),scale=unreal.Vector(*scale)),False)
for x in range(-400,8800,120):
    for y in range(-1200,401,120):
        instance(cube,ivory if (x//120+y//120)%2 else rose,(x,y,-395),(1.13,1.13,.025))
for y in (150,-150,-450,-750,-1050):
    for j,x in enumerate(range(100,8250,55)):instance(sphere,coral if j%4<2 else rope,(x,y,5),(.32,.32,.25))
for y in (0,-300,-600,-900):
    for x in range(200,8100,450):instance(cube,deep,(x,y,-389),(3.7,.12,.025))
    shape(cube,'Starting block',(0,y,155),(1.2,1.4,.4),ivory);shape(cube,'Starting block base',(-15,y,85),(.5,.65,1),deep)
    shape(cube,'Finish timing pad',(8210,y,-95),(.12,2.8,2.3),deep)
# Poolside architecture: repeated tall open windows, brass ribs and dusk beyond.
sky=A.load_asset('/Game/DreamSeeker/Levels/FirstRipple/Polish/Materials/M_MemorySky')
shape(sphere,'Sunset outside the pool',(4200,-8000,2400),(320,320,320),sky)
shape(sphere,'Low sun beyond the windows',(3600,-9000,1500),(12,2,12),light)
shape(cube,'Lower rear wall',(4200,-2100,420),(94,1.5,7.5),tile)
shape(cube,'Rear cornice',(4200,-2100,1980),(94,2,.65),gold)
for x in range(-350,9000,850):
    shape(cube,'Stone window pier',(x,-2070,1210),(1.35,2.5,17),ivory)
    shape(cube,'Window amber glass',(x+420,-2120,1330),(6.6,.035,11),glass)
    for dx in (180,420,660):beam('Window mullion',(x+dx,-2040,760),(x+dx,-2040,1900),12,gold)
    beam('Window transom',(x+95,-2040,1250),(x+745,-2040,1250),12,gold)
    beam('Window sill',(x+70,-2040,750),(x+770,-2040,750),28,ivory)
    # Vault ribs curve overhead while leaving the camera side open.
    points=[]
    for j in range(11):
        angle=math.pi*j/10;points.append((x,-650+1550*math.cos(angle),1900+850*math.sin(angle)))
    for a,b in zip(points,points[1:]):beam('Vault brass rib',a,b,28,gold)
    for side in (-1,1):shape(cube,'Gallery balustrade',(x+420,-1740,700),(8,.12,.3),gold)
    for dx in range(100,780,90):instance(cylinder,gold,(x+dx,-1740,555),(.06,.06,2.8))
    shape(cube,'Gallery platform',(x+420,-1900,400),(8.3,3.5,.5),deep)
    for j in range(6):
        xx=x+120+j*112+random.uniform(-18,18);h=random.uniform(125,175)
        instance(sphere,silhouette,(xx,-1960,465+h*.45),(.55,.38,h/100))
        instance(sphere,silhouette,(xx,-1960,470+h),(.42,.42,.42))
    for j in range(10):
        instance(sphere,leaf,(x+random.uniform(-50,55),-1880,1800-j*80),(random.uniform(.3,.7),.12,.3),rot=(0,random.uniform(-25,25),0))
    # Wall lamps and warm glowing globes.
    shape(sphere,'Gallery globe',(x,-1840,1050),(.45,.45,.65),light)
for x in range(7600,8350,90):
    for j,y in enumerate(range(-1080,201,90)):instance(cube,deep if (x//90+j)%2 else ivory,(x,y,-388),(.86,.86,.03))
for y in range(-1100,251,150):
    shape(cube,'Finish flag',(8000,y,300),(.45,.8,.8),coral if y%300 else ivory)
beam('Finish flag line',(8000,-1220,350),(8000,360,350),5,gold)
text('Race title','AGAINST THE TIDE',(1450,-1600,1090),68)
text('Finish sign','FINISH',(8010,-1150,540),55)
text('Race rule inscription','ONE LENGTH. FIND YOUR RHYTHM.',(900,-1320,190),30)
sun=spawn(unreal.DirectionalLight,'Sunset through the gallery',(0,1000,2000));c=sun.get_component_by_class(unreal.DirectionalLightComponent);c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_intensity(2);c.set_light_color(unreal.LinearColor(1,.56,.30));sun.set_actor_rotation(unreal.Rotator(0,-18,-50),False)
fill=spawn(unreal.SkyLight,'Cool pool fill',(4200,-800,1700));c=fill.get_component_by_class(unreal.SkyLightComponent);c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_editor_property('real_time_capture',True);c.set_intensity(.40)
start=spawn(unreal.PlayerStart,'Start in foreground lane',(350,0,-45))
director=spawn(A.load_blueprint_class(ROOT+'/BP_RaceDirector'),'Race director',(350,0,100))
for i,mat in enumerate((coral,cream,violet),1):
    rival=spawn(A.load_blueprint_class(ROOT+'/BP_RaceRival'),'Rival '+str(i),(350,-300*i,-38));rival.set_editor_property('LaneY',-300*i);rival.set_editor_property('RaceStyle',i)
    for c in rival.get_components_by_class(unreal.StaticMeshComponent):
        if c.get_name() in ('RaceCap','Body'):c.set_material(0,mat)
    director.set_editor_property('Rival'+str(i),rival)
completion=spawn(A.load_blueprint_class(HUB+'/BP_DreamCompletion'),'Race victory awards second seal',(8200,0,0));completion.set_editor_property('SaveSlot','DreamSeeker.Memory.02')
spawn(A.load_blueprint_class(HUB+'/BP_ReturnToMemoryHub'),'Return to hub with B',(350,0,0))
assert unreal.EditorLoadingAndSavingUtils.save_map(world,MAP)
# Only replace the second cloud destination; preserve the team's original map.
assert levels.load_level('/Game/Dreamhub_MemoryCauseway')
for a in actors.get_all_level_actors():
    if a.get_actor_label()=='Memory 2 entrance':a.set_editor_property('destination',A.load_asset(MAP))
assert levels.save_current_level()
unreal.log('RACE_SCENE_READY detail_batches='+str(len(batches)))
