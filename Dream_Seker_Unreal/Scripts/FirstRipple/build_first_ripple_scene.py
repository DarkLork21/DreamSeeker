"""Create the complete first-dream route without replacing the team's original map."""
import unreal,math,random,json
from pathlib import Path
A=unreal.EditorAssetLibrary;L=unreal.BlueprintEditorLibrary
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
tools=unreal.AssetToolsHelpers.get_asset_tools();edit=unreal.MaterialEditingLibrary
sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);data=unreal.SubobjectDataBlueprintFunctionLibrary
ROOT='/Game/DreamSeeker/Levels/FirstRipple';MAP=ROOT+'/LV_FirstRipple';SWIM='/Game/DreamSeeker/Swimming'
HUB='/Game/DreamSeeker/DreamHub/MemoryCauseway'
random.seed(19)

def material(name,rgb,glow=0,alpha=None):
    path=ROOT+'/Materials/'+name
    if A.does_asset_exist(path):return A.load_asset(path)
    m=tools.create_asset(name,ROOT+'/Materials',unreal.Material,unreal.MaterialFactoryNew());m.set_editor_property('two_sided',True)
    c=edit.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-320,0);c.set_editor_property('constant',unreal.LinearColor(*(v*(glow or 1) for v in rgb),1))
    prop=unreal.MaterialProperty.MP_BASE_COLOR
    if glow or alpha is not None:m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT);prop=unreal.MaterialProperty.MP_EMISSIVE_COLOR
    assert edit.connect_material_property(c,'',prop)
    if alpha is not None:
        m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT)
        opacity=edit.create_material_expression(m,unreal.MaterialExpressionConstant,-320,180);opacity.set_editor_property('r',alpha)
        assert edit.connect_material_property(opacity,'',unreal.MaterialProperty.MP_OPACITY)
    edit.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES)
    edit.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_NANITE)
    edit.recompile_material(m);assert A.save_loaded_asset(m,False);return m

wood=material('M_HomeTimber',(.26,.12,.055));trim=material('M_SunBleachedWood',(.53,.37,.20))
roof=material('M_WeatheredSlate',(.13,.20,.19));soil=material('M_Silt',(.17,.22,.16))
green=material('M_ReedGreen',(.19,.28,.11));leaf=material('M_WillowLeaf',(.18,.25,.10));bark=material('M_WillowBark',(.12,.085,.05))
glow=material('M_LanternGold',(1,.62,.20),3);mist=material('M_DreamMist',(.22,.32,.40),1,.08)
water=material('M_LakeWater',(.035,.23,.26),1,.10);line=material('M_SurfaceLight',(.40,.65,.56),.7)
sky=material('M_DuskSky',(.12,.22,.29),1);sunmat=material('M_LowSun',(1,.64,.25),2)
blue=material('M_NaiaDress',(.12,.35,.40));hair=material('M_NaiaHair',(.045,.025,.018));skin=material('M_NaiaSkin',(.58,.34,.21))
textmat=A.load_asset(HUB+'/Materials/M_LegibleMemoryText')
cube=A.load_asset('/Engine/BasicShapes/Cube');sphere=A.load_asset('/Engine/BasicShapes/Sphere');cyl=A.load_asset('/Engine/BasicShapes/Cylinder');cone=A.load_asset('/Engine/BasicShapes/Cone')

def spawn(cls,name,xyz,folder,rot=(0,0,0)):
    a=actors.spawn_actor_from_class(cls,unreal.Vector(*xyz),unreal.Rotator(*rot));a.set_actor_label(name);a.set_folder_path(unreal.Name('First Ripple / '+folder));return a
def shape(mesh,name,xyz,scale,mat=None,solid=False,rot=(0,0,0),folder='Scenery'):
    a=spawn(unreal.StaticMeshActor,name,xyz,folder,rot);c=a.static_mesh_component;c.set_static_mesh(mesh)
    if mat:c.set_material(0,mat)
    c.set_collision_profile_name('BlockAll' if solid else 'NoCollision');c.set_cast_shadow(solid)
    a.set_actor_scale3d(unreal.Vector(*scale));return a
def beam(name,start,end,width,mat,folder='Scenery',solid=False):
    a=unreal.Vector(*start);b=unreal.Vector(*end);d=b-a;r=unreal.MathLibrary.find_look_at_rotation(a,b)
    return shape(cube,name,((a.x+b.x)/2,(a.y+b.y)/2,(a.z+b.z)/2),(d.length()/100,width/100,width/100),mat,solid,(r.roll,r.pitch,r.yaw),folder)
def text(name,label,xyz,size=32):
    a=spawn(unreal.TextRenderActor,name,xyz,'Tutorial',(0,0,90));c=a.text_render;c.set_text(label);c.set_world_size(size);c.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER);c.set_text_material(textmat);c.set_text_render_color(unreal.Color(221,218,181,255));return a
def lamp(name,x,y,z):
    beam(name+' post',(x,y,z-125),(x,y,z+50),10,trim,'Lanterns')
    shape(cube,name+' cage',(x,y,z+15),(.30,.30,.48),wood,folder='Lanterns')
    shape(sphere,name+' flame',(x,y+19,z+15),(.17,.13,.29),glow,folder='Lanterns')
    a=spawn(unreal.PointLight,name+' light',(x,y+40,z+10),'Lighting');c=a.get_component_by_class(unreal.PointLightComponent);c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_intensity(2200);c.set_light_color(unreal.LinearColor(1,.64,.30,1));c.set_attenuation_radius(650)

assert not A.does_asset_exist(MAP),'First Ripple exists; do not overwrite a reviewed level'
world=unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.GameModeBase)
mode=tools.create_asset('BP_FirstRippleMode',ROOT,unreal.Blueprint,factory);L.compile_blueprint(mode)
unreal.get_default_object(mode.generated_class()).set_editor_property('default_pawn_class',A.load_blueprint_class(SWIM+'/BP_RhythmSwimmer'));assert A.save_loaded_asset(mode,False)
world.get_world_settings().set_editor_property('default_game_mode',mode.generated_class())

# Wide scenic depth; gameplay remains in the X/Z swimming plane.
shape(sphere,'Dusk over the lake',(5000,0,3000),(420,420,420),sky,folder='Atmosphere')
shape(sphere,'Sun remembered through the willow',(-1600,-6500,2200),(6,1,6),sunmat,folder='Atmosphere')
for i in range(16):
    x=-1600+i*900
    shape(sphere,'Far hills '+str(i),(x,-5000,350+random.random()*200),(13+random.random()*8,10,8+random.random()*7),roof,folder='Distant shore')
    shape(sphere,'Cloud reflection '+str(i),(x,-3000,1100+random.random()*700),(10+random.random()*9,5,1.8),mist,folder='Atmosphere')
sun=spawn(unreal.DirectionalLight,'Late afternoon sunlight',(-1500,2000,2300),'Lighting',(0,-35,-35))
dc=sun.get_component_by_class(unreal.DirectionalLightComponent);dc.set_mobility(unreal.ComponentMobility.MOVABLE);dc.set_intensity(3.5);dc.set_light_color(unreal.LinearColor(1,.83,.62,1))
fill=spawn(unreal.SkyLight,'Soft lakeside sky',(5000,0,1800),'Lighting');sc=fill.get_component_by_class(unreal.SkyLightComponent);sc.set_mobility(unreal.ComponentMobility.MOVABLE);sc.set_editor_property('real_time_capture',True);sc.set_intensity(.8)

# Water volume and a visible bed; narrow surface strokes remain legible from the camera.
shape(cube,'Continuous water',(5500,-100,-250),(114,17,5),water,folder='Water')
shape(cube,'Visible riverbed',(5500,-200,-560),(120,22,1.2),soil,True,folder='Collision')
for x in range(-200,11401,130):
    beam('Surface glint',(x,210,0),(x+random.uniform(35,100),210,0),2,line,'Water')
for x in (-50,11150):
    wall=shape(cube,'Swim boundary',(x,0,-220),(.25,12,7),None,True,folder='Collision');wall.set_actor_hidden_in_game(True)

# Home is a real small timber set, constructed in depth behind the starting shore.
shape(cube,'Home stone foundation',(-250,-640,40),(13,9,1.4),soil,True,folder='Home')
shape(cube,'Home timber walls',(-250,-700,440),(11,7,7),wood,folder='Home')
for z in range(130,790,48):
    beam('Home siding',(-800,-330,z),(300,-330,z),26,trim,'Home')
for x in (-790,290):beam('Home corner post',(x,-310,80),(x,-310,820),34,bark,'Home')
for side in (-1,1):shape(cube,'Pitched roof',(-250,-700+side*230,900),(13,5.5,.32),roof,rot=(side*27,0,0),folder='Home')
for x in (-540,60):
    shape(cube,'Warm window frame',(x,-283,510),(2.8,.18,3.1),bark,folder='Home')
    shape(cube,'Warm window light',(x,-268,510),(2.3,.08,2.6),glow,folder='Home')
    beam('Window mullion',(x,-250,380),(x,-250,640),12,wood,'Home')
    beam('Window crossbar',(x-120,-250,500),(x+120,-250,500),12,wood,'Home')
shape(cube,'Blue front door',(-240,-260,290),(1.7,.22,4.2),roof,folder='Home')
for i in range(5):shape(cube,'Home steps',(-250+i*80,-110,80-i*25),(1.1,3.7,.25),trim,folder='Home')
for i in range(20):shape(cube,'Home landing plank',(-400+i*50,-100,0),(.45,5,.12),trim,folder='Home')
lamp('Porch lantern',150,-190,520)

# A willow frames home. Its branches are hand-built geometry rather than image planes.
beam('Old willow trunk',(-970,-950,10),(-800,-900,1350),100,bark,'Willow')
for end in ((-1700,-780,1250),(200,-900,1500),(700,-1100,1050),(-500,-1200,1700)):
    beam('Willow bough',(-850,-900,980),end,45,bark,'Willow')
    for j in range(5):
        x=end[0]+random.uniform(-260,260);y=end[1]+random.uniform(-160,160);z=end[2]+random.uniform(-150,150)
        shape(sphere,'Willow canopy',(x,y,z),(4.3,2.1,1.7),leaf,folder='Willow')
        beam('Hanging willow',(x,y,z),(x+40,y,z-random.uniform(350,600)),9,green,'Willow')

# The five sections are a single connected lake, with rest landings and visual anchors.
for x in (1800,3800,6900,9200,10650):
    for i in range(8):shape(cube,'Landing board',(x+i*45,-360,15),(.42,5,.13),trim,folder='Landings')
    for dx in (0,300):beam('Landing support',(x+dx,-420,-520),(x+dx,-420,10),22,bark,'Landings')
    lamp('Shore beacon',x+260,-380,155)
for x in (2550,3000,3450):shape(cube,'Floating rhythm marker',(x,0,12),(.85,1.8,.23),trim,folder='Rhythm pool')
# A surface blockage with enough clearance below it to teach intentional diving.
log=shape(cyl,'Fallen willow - dive beneath',(5400,-80,-45),(1.5,4.4,11),bark,True,(0,90,0),'First dive')
for x in (5000,5400,5800):
    beam('Fallen willow branch',(x,-230,30),(x+200,-450,270),24,bark,'First dive')
    shape(sphere,'Leaf caught on the log',(x+220,-470,280),(1.8,1.5,.7),leaf,folder='First dive')
# A visible under-log opening and a soft underwater trail, not a hidden pixel gap.
for x,z in ((4550,-180),(4900,-280),(5350,-300),(5800,-270),(6300,-170)):
    shape(sphere,'Underwater glimmer',(x,180,z),(.035,.035,.035),line,folder='First dive')
for x in range(7500,8600,170):
    beam('Current streak',(x,180,-50),(x+90,180,-65),3,line,'Current')

# Reuse the team's existing underwater meshes for the lakebed.
rockmeshes=[A.load_asset('/Game/StylizedUnderwater/Meshes/Rocks/'+n) for n in ('smallRock1','smallRock2','MediumRock1','ShapeRock')]
grass=A.load_asset('/Game/StylizedUnderwater/Meshes/Grass/Grass')
for i in range(85):
    x=random.uniform(700,10900);y=random.choice((-450,350))+random.uniform(-120,120)
    mesh=random.choice(rockmeshes)
    if mesh:shape(mesh,'River stone',(x,y,-490),(random.uniform(.35,.9),random.uniform(.4,.9),random.uniform(.4,.9)),folder='Riverbed')
for i in range(70):
    x=random.uniform(1000,11000);y=random.choice((-650,430));z=-450 if y>0 else 0
    if grass:shape(grass,'Water grass',(x,y,z),(1.8,1.8,2.5),folder='Riverbed')
    if i%2==0:
        for j in range(3):
            xx=x+j*22;beam('Reed stalk',(xx,-620,0),(xx+random.uniform(-40,40),-620,random.uniform(150,290)),6,green,'Reeds')
            shape(cyl,'Reed seed head',(xx,-620,260),(.10,.10,.6),bark,folder='Reeds')
for i in range(9):
    shape(sphere,'Dream cloud beyond the shore',(9300+i*350,-1700,450+i*80),(5.5,3,1.2),mist,folder='Dream horizon')
    shape(cube,'Unremembered landing fragment',(9800+i*220,-1500,550+i*70),(1.3,1.6,.12),trim,folder='Dream horizon')

text('First memory title','THE FIRST RIPPLE',(550,180,590),42)
text('Home lesson','By home, the water was gentle.',(700,180,450),25)
text('Kick instruction','A  LEFT KICK     D  RIGHT KICK',(1050,210,290),25)
text('Steer instruction','POINT WITH THE MOUSE TO SWIM',(1050,210,230),23)
text('Rhythm instruction','ALTERNATE. FIND A STEADY RHYTHM.',(2950,210,300),25)
text('Lucidity instruction','GOOD RHYTHM SLOWLY RESTORES LUCIDITY',(2950,210,235),21)
text('Dive instruction','AIM BELOW THE FALLEN WILLOW',(4900,210,330),26)
text('Sprint instruction','HOLD SHIFT TO SWIM HARDER',(7700,210,330),27)
text('Sprint cost','SPRINTING SPENDS LUCIDITY. KEEP YOUR RHYTHM.',(7700,210,265),21)
text('Finish instruction','REACH THE LANTERN. YOUR FIRST CROSSING.',(10200,210,400),25)

start=spawn(unreal.PlayerStart,'Naia starts in the home shallows',(250,0,-45),'Gameplay')
completion=spawn(A.load_blueprint_class(HUB+'/BP_DreamCompletion'),'First independent crossing completion',(10600,0,0),'Gameplay');completion.set_editor_property('SaveSlot','DreamSeeker.Memory.01')
spawn(A.load_blueprint_class(HUB+'/BP_ReturnToMemoryHub'),'B - return without completing',(0,0,0),'Gameplay')
assert unreal.EditorLoadingAndSavingUtils.save_map(world,MAP)

# A simple authored character proxy keeps the first playable independent of unfinished character art.
bp=A.load_asset(SWIM+'/BP_RhythmSwimmer');root=sub.k2_gather_subobject_data_for_blueprint(bp)[0]
for name,mesh,xyz,scale,mat,rotation in (
    ('Naia head',sphere,(0,0,26),(.24,.21,.25),skin,(0,0,0)),
    ('Naia hair',sphere,(-6,-1,31),(.24,.23,.23),hair,(0,0,0)),
    ('Naia dress',cone,(-10,0,-2),(.32,.21,.45),blue,(0,-65,0)),
    ('Naia left leg',cyl,(-28,7,-23),(.07,.07,.33),skin,(0,65,0)),
    ('Naia right leg',cyl,(-26,-7,-18),(.07,.07,.34),skin,(0,90,0)),
    ('Naia reaching arm',cyl,(18,8,3),(.06,.06,.32),skin,(0,80,0))):
    h,error=sub.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root,new_class=unreal.StaticMeshComponent,blueprint_context=bp));assert not str(error)
    sub.rename_subobject(h,unreal.Text(name));c=data.get_object_for_blueprint(data.get_data(h),bp);c.set_static_mesh(mesh);c.set_material(0,mat);c.set_collision_profile_name('NoCollision');c.set_editor_property('relative_location',unreal.Vector(*xyz));c.set_editor_property('relative_scale3d',unreal.Vector(*scale));c.set_editor_property('relative_rotation',unreal.Rotator(*rotation))
L.compile_blueprint(bp);assert A.save_loaded_asset(bp,False)

# Make the first cloud enter the new dream, leaving the original team map accessible.
assert levels.load_level('/Game/Dreamhub_MemoryCauseway')
for actor in actors.get_all_level_actors():
    if actor.get_actor_label()=='Memory 1 entrance':actor.set_editor_property('Destination',A.load_asset(MAP))
assert levels.save_current_level()
Path(unreal.Paths.project_saved_dir(),'FirstRippleBuild.json').write_text(json.dumps({'map':MAP,'route_length':10850,'sections':5,'uses_team_lucidity':True,'original_level_preserved':'/Game/Level_1_Learning'},indent=2))
unreal.log('FIRST_RIPPLE_SCENE_BUILT')
