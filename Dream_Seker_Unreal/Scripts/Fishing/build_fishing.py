"""Author the fishing Blueprints and place only gameplay actors in Level 3."""
from pathlib import Path
import unreal

# Share the node-authoring helpers with the swimming scripts without running their builders.
source = Path(__file__).resolve().parents[1] / 'FirstRipple/build_first_ripple_gameplay.py'
exec(source.read_text(encoding='utf-8').split("path=ROOT+'/BP_RhythmSwimmer'")[0])

ROOT = '/Game/DreamSeeker/Levels/Fishing'
MAP = '/Game/Level_3_Fishing'
LEVELS = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ACTORS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LUCIDITY = '/Game/DreamSeeker/Blueprints/Components/BPC_Lucidity.BPC_Lucidity_C'
WIDGET = '/Game/DreamSeeker/UI/WBP_LucidityBar.WBP_LucidityBar_C'
CENTER, PLANE, START, BOTTOM = -2800, 1380, 9150, 1270


def blueprint(name, parent=None, template=None):
    path = ROOT + '/' + name
    if A.does_asset_exist(path):
        return A.load_asset(path)
    if template:
        return check(A.duplicate_asset(template, path), path)
    factory = unreal.BlueprintFactory()
    factory.set_editor_property('parent_class', parent)
    return check(unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        name, ROOT, unreal.Blueprint, factory), path)


def class_path(bp):
    return bp.get_path_name() + '_C'


def graph(bp, clear=True):
    result = unreal.BlueprintGraphEditor.get_graph_editor(L.find_event_graph(bp))
    if clear:
        result.remove_nodes(result.list_all_nodes())
    return result


def properties(bp, mapping):
    for name, value in mapping.items():
        kind = 'bool' if isinstance(value, bool) else 'real'
        L.add_member_variable(bp, name, L.get_basic_type_by_name(kind))
        L.set_blueprint_variable_instance_editable(bp, name, True)
    L.compile_blueprint(bp)
    cdo = unreal.get_default_object(bp.generated_class())
    for name, value in mapping.items():
        cdo.set_editor_property(name, value)


def cast(builder, execute, value, kind, cls):
    node = builder.pos(builder.g.create_node_from_name(
        'Utilities|Casting|CastTo' + kind.static_class().get_name(), unreal.Vector2D(), []))
    check(builder.g.retarget_node_class(node, kind.static_class(), cls), 'cast ' + cls.get_name())
    builder.link(execute, node.find_execute_pin())
    builder.link(value, node.find_input_pin('Object'))
    typed = next(pin for pin in node.list_output_pins() if str(pin.get_pin_name()).startswith('As'))
    return node.find_then_pin(), typed


def call_on(builder, execute, name, obj, **args):
    node = builder.do(execute, name, **args)
    builder.link(obj, node.find_self_pin())
    return node


def vector(builder, **axes):
    return builder.math('MakeVector', **axes)


def player(builder):
    return builder.call('GameplayStatics.GetPlayerPawn').find_output_pin('ReturnValue')


def time(builder):
    return builder.call('GameplayStatics.GetTimeSeconds').find_output_pin('ReturnValue')


def math2(builder, op, a, b):
    return builder.math(op + '_DoubleDouble', A=a, B=b)


def add(builder, a, b):
    return math2(builder, 'Add', a, b)


def subtract(builder, a, b):
    return math2(builder, 'Subtract', a, b)


def multiply(builder, a, b):
    return math2(builder, 'Multiply', a, b)


pawn = blueprint('BP_FishingLure', template=HUB + '/BP_MemoryWisp')
P = class_path(pawn)
g = graph(pawn, False)
g.remove_nodes([n for n in g.list_all_nodes() if
                (n.get_node_pos().y < 2900 and 'BeginPlay' not in str(n.get_node_title()).replace(' ', ''))
                or n.get_node_pos().y >= 5000])
properties(pawn, {'AttemptEnded': False, 'LastFishHit': -10.0, 'ReleaseAt': 0.0,
                  'SteeringAxis': 0.0})
handles = sub.k2_gather_subobject_data_for_blueprint(pawn)
components = [data.get_object_for_blueprint(data.get_data(h), pawn) for h in handles]
for component in components:
    if isinstance(component, unreal.StaticMeshComponent):
        component.set_editor_property('visible', False)
    if isinstance(component, unreal.CameraComponent):
        component.set_editor_property('relative_location', unreal.Vector(0,-1960,0))
        component.set_editor_property('relative_rotation', unreal.Rotator(0,0,90))
        component.set_editor_property('projection_mode', unreal.CameraProjectionMode.PERSPECTIVE)
        component.set_editor_property('field_of_view', 78.0)
        component.set_editor_property('use_pawn_control_rotation', False)
if not any(c and c.get_class().get_name() == 'BPC_Lucidity_C' for c in components):
    component, error = sub.add_new_subobject(unreal.AddNewSubobjectParams(
        parent_handle=handles[0], new_class=A.load_blueprint_class(LUCIDITY.split('.')[0]),
        blueprint_context=pawn))
    check(not str(error), str(error))
    sub.rename_subobject(component, unreal.Text('Lucidity'))

def lure_material(name, color):
    path = ROOT + '/' + name
    material = A.load_asset(path) if A.does_asset_exist(path) else (
        unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            name, ROOT, unreal.Material, unreal.MaterialFactoryNew()))
    editing = unreal.MaterialEditingLibrary
    editing.delete_all_material_expressions(material)
    material.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT)
    tint = editing.create_material_expression(material,unreal.MaterialExpressionConstant3Vector,-210,0)
    tint.set_editor_property('constant',unreal.LinearColor(*color,1))
    check(editing.connect_material_property(tint,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR),name)
    editing.recompile_material(material)
    check(A.save_loaded_asset(material,False),name)
    return material


bright = lure_material('M_FishingLure',(.96,.26,.12))
pale = lure_material('M_FishingLine',(.42,.61,.7))
# The bobber, line, and hook sit on the pawn and never alter scene lighting.
for name, mesh, offset, scale, pitch, material in [
    ('LureBobber','Sphere',(0,0,0),(.69,.69,.83),0,bright),
    ('FishingLine','Cylinder',(0,0,550),(.026,.026,11),0,pale),
    ('HookStem','Cylinder',(0,0,-52),(.065,.065,.54),0,pale),
    ('HookBend','Cylinder',(-13,0,-75),(.065,.065,.34),57,pale),
    ('HookPoint','Cylinder',(-25,0,-67),(.06,.06,.28),-20,pale),
]:
    mesh_component = next((c for c in components if c and
                           c.get_name().startswith(name+'_')),None)
    if mesh_component is None:
        h, error = sub.add_new_subobject(unreal.AddNewSubobjectParams(
            parent_handle=handles[0], new_class=unreal.StaticMeshComponent, blueprint_context=pawn))
        check(not str(error), str(error))
        sub.rename_subobject(h, unreal.Text(name))
        mesh_component = data.get_object_for_blueprint(data.get_data(h), pawn)
    mesh_component.set_static_mesh(A.load_asset('/Engine/BasicShapes/' + mesh))
    mesh_component.set_material(0,material)
    mesh_component.set_editor_property('visible',True)
    mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    mesh_component.set_editor_property('relative_location',unreal.Vector(*offset))
    mesh_component.set_editor_property('relative_rotation',unreal.Rotator(0,pitch,0))
    mesh_component.set_editor_property('relative_scale3d',unreal.Vector(*scale))
    mesh_component.set_editor_property('cast_shadow',False)

L.compile_blueprint(pawn)
G = Graph(g, 5100)
controller = G.call('GameplayStatics.GetPlayerController').find_output_pin('ReturnValue')
cursor = next(n for n in g.list_all_nodes() if tuple((n.get_node_pos().x,n.get_node_pos().y)) == (600,4200))
cursor.find_then_pin().break_pin_links()
move = G.read('CharacterMovement')
e = call_on(G, cursor.find_then_pin(), 'CharacterMovementComponent.SetMovementMode',
            move, NewMovementMode='MOVE_None').find_then_pin()
e = G.do(e, 'Actor.K2_SetActorLocation', NewLocation=f'{CENTER},{PLANE},{START}').find_then_pin()
e = G.do(e, 'Actor.K2_SetActorRotation', NewRotation='0,0,0').find_then_pin()
e = G.set(e, 'ReleaseAt', add(G,time(G),'1.2'))
widget = G.do(e, '/Script/UMG.WidgetBlueprintLibrary.Create', WidgetType=WIDGET, OwningPlayer=controller)
e, typed = cast(G, widget.find_then_pin(), widget.find_output_pin('ReturnValue'), unreal.Character,
                A.load_blueprint_class(WIDGET.split('.')[0]))
e = G.set(e, 'LucidityComponent', G.read('Lucidity'), WIDGET, typed)
call_on(G, e, '/Script/UMG.UserWidget.AddToViewport', typed)

tick = L.add_event_override(pawn, 'ReceiveTick', unreal.IntPoint(0, 7200))
T = Graph(g, 7500)
dt = tick.find_output_pin('DeltaSeconds')
wait = T.math('BooleanOR', A=T.read('AttemptEnded'),
              B=math2(T,'Less',time(T),T.read('ReleaseAt')))
waiting = T.pos(g.add_branch_node())
T.put(waiting.find_input_pin('Condition'), wait)
active = waiting.find_else_pin()
axes = T.call('KismetMathLibrary.BreakVector', InVec=T.call('Actor.K2_GetActorLocation').find_output_pin('ReturnValue'))
for key, variable, y in [('A','MoveLeft',6800),('D','MoveRight',7050)]:
    binding = G.key(key,y)
    G.set(binding.find_output_pin('Pressed'),variable,'true')
    G.set(binding.find_output_pin('Released'),variable,'false')

def key_axis(variable):
    return T.math('SelectFloat',A='1',B='0',bPickA=T.read(variable))

steer = subtract(T,key_axis('MoveLeft'),key_axis('MoveRight'))
smoothed = T.math('FInterpTo', Current=T.read('SteeringAxis'), Target=steer,
                  DeltaTime=dt, InterpSpeed='15')
active = T.set(active, 'SteeringAxis', smoothed)
x = T.math('FClamp', Value=add(T,axes.find_output_pin('X'),multiply(T,T.read('SteeringAxis'),multiply(T,dt,'830'))),
           Min=str(CENTER-1040), Max=str(CENTER+1040))
z = T.math('FMax', A=subtract(T,axes.find_output_pin('Z'),multiply(T,dt,'440')), B=str(BOTTOM))
T.do(active, 'Actor.K2_SetActorLocation', NewLocation=vector(T,X=x,Y=str(PLANE),Z=z))

# Damage and completion use public Blueprint functions called by the fish actors.
for raw in L.list_graphs(pawn):
    if raw.get_name() in ('HitObstacle', 'HookTarget'):
        L.remove_function_graph(pawn, raw.get_name())
L.compile_blueprint(pawn)
hit = unreal.BlueprintGraphEditor.create_and_edit_function_graph(pawn, 'HitObstacle')
hit.set_function_is_public()
F = Graph(hit, 200)
ready = F.math('BooleanAND', A=F.math('Not_PreBool', A=F.read('AttemptEnded')),
               B=math2(F,'GreaterEqual',subtract(F,time(F),F.read('LastFishHit')),'.85'))
e = F.branch(hit.find_graph_entry_pin(), ready).find_then_pin()
e = F.set(e, 'LastFishHit', time(F))
call_on(F,e,LUCIDITY+':ConsumeLucidity',F.read('Lucidity'),Amount='25')
catch = unreal.BlueprintGraphEditor.create_and_edit_function_graph(pawn, 'HookTarget')
catch.set_function_is_public()
F = Graph(catch, 200)
e = F.branch(catch.find_graph_entry_pin(), F.math('Not_PreBool', A=F.read('AttemptEnded'))).find_then_pin()
e = F.set(e, 'AttemptEnded', 'true')
complete_bp = A.load_asset(HUB+'/BP_DreamCompletion')
complete_path = class_path(complete_bp)
n = F.do(e, 'GameplayStatics.GetActorOfClass', ActorClass=complete_path)
e, completion = cast(F,n.find_then_pin(),n.find_output_pin('ReturnValue'),unreal.Actor,complete_bp.generated_class())
call_on(F,e,complete_path+':CompleteDream',completion)

# Follow the swimming retry pattern: stop the attempt, show failure, reload the current map.
hp = T.read('CurrentLucidity', LUCIDITY, T.read('Lucidity'))
death = T.branch(tick.find_then_pin(), math2(T,'LessEqual',hp,'0'))
T.link(death.find_else_pin(), waiting.find_execute_pin())
failed = T.branch(death.find_then_pin(),T.math('Not_PreBool',A=T.read('AttemptEnded')))
e = T.set(failed.find_then_pin(),'AttemptEnded','true')
e = T.do(e,'KismetSystemLibrary.Delay',Duration='1.65').find_then_pin()
T.do(e,'GameplayStatics.OpenLevelBySoftObjectPtr',Level=MAP+'.Level_3_Fishing')
compile_save(pawn)


fish = blueprint('BP_FishingFish', unreal.StaticMeshActor)
g = graph(fish)
properties(fish, {'LaneCenter': float(CENTER), 'DepthZ': 0.0, 'PatrolWidth': 0.0,
                  'PatrolRate': 1.0, 'Phase': 0.0, 'HookRadius': 135.0,
                  'BodyHeight': 105.0, 'IsTarget': False, 'WasTouching': False})
component = unreal.get_default_object(fish.generated_class()).get_component_by_class(unreal.StaticMeshComponent)
component.set_mobility(unreal.ComponentMobility.MOVABLE)
component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
tick = L.add_event_override(fish,'ReceiveTick',unreal.IntPoint())
F = Graph(g, 200)
angle = add(F,multiply(F,time(F),F.read('PatrolRate')),F.read('Phase'))
x = add(F,F.read('LaneCenter'),multiply(F,F.read('PatrolWidth'),F.math('Sin',A=angle)))
location = vector(F,X=x,Y=str(PLANE),Z=F.read('DepthZ'))
move = F.do(tick.find_then_pin(),'Actor.K2_SetActorLocation',NewLocation=location)
facing = F.math('SelectFloat', A='180', B='0', bPickA=math2(F,'Less',F.math('Cos',A=angle),'0'))
facing = F.math('SelectFloat', A='0', B=facing, bPickA=F.read('IsTarget'))
rotation = F.math('MakeRotator', Yaw=facing)
e = F.do(move.find_then_pin(),'Actor.K2_SetActorRotation',NewRotation=rotation).find_then_pin()
e,lure = cast(F,e,player(F),unreal.Actor,pawn.generated_class())
loc = F.call('Actor.K2_GetActorLocation')
F.link(lure,loc.find_self_pin())
xyz = F.call('KismetMathLibrary.BreakVector',InVec=loc.find_output_pin('ReturnValue'))
# Elliptical hit area follows the fish silhouette instead of its full mesh box.
def normalized_axis(axis, center, size):
    offset = subtract(F,xyz.find_output_pin(axis),center)
    ratio = math2(F,'Divide',offset,F.read(size))
    return multiply(F,ratio,ratio)
radius = add(F,normalized_axis('X',x,'HookRadius'),
             normalized_axis('Z',F.read('DepthZ'),'BodyHeight'))
inside = math2(F,'LessEqual',radius,'1')
new_hit = F.math('BooleanAND',A=inside,B=F.math('Not_PreBool',A=F.read('WasTouching')))
contact = F.branch(e,new_hit)
F.set(contact.find_else_pin(),'WasTouching',inside)
e = F.set(contact.find_then_pin(),'WasTouching','true')
target = F.branch(e,F.read('IsTarget'))
call_on(F,target.find_then_pin(),P+':HookTarget',lure)
call_on(F,target.find_else_pin(),P+':HitObstacle',lure)
compile_save(fish)

hud = blueprint('BP_FishingHUD', unreal.HUD)
g = graph(hud)
H = Graph(g, 200)
draw = L.add_event_override(hud,'ReceiveDrawHUD',unreal.IntPoint())
e,lure = cast(H,draw.find_then_pin(),player(H),unreal.Actor,pawn.generated_class())
panel_y = '18'
width = subtract(H,draw.find_output_pin('SizeX'),'48')
e = H.do(e,'HUD.DrawRect',RectColor='(R=.015,G=.035,B=.06,A=.86)',
         ScreenX='24',ScreenY=panel_y,ScreenW=width,ScreenH='54').find_then_pin()
hit_recent = math2(H,'Less',subtract(H,time(H),H.read('LastFishHit',P,lure)),'.75')
msg = H.math('SelectString',A='LUCIDITY LOST  |  Dodge the other fish',
             B='A / D  Steer     |     Hook the large orange clownfish     |     B  Return',bPickA=hit_recent)
color = H.math('SelectColor',A='(R=1,G=.45,B=.39,A=1)',B='(R=1,G=.91,B=.74,A=1)',bPickA=hit_recent)
e = H.do(e,'HUD.DrawText',Text=msg,TextColor=color,ScreenX='42',
         ScreenY='34',Scale='1.35').find_then_pin()
failed = H.math('BooleanAND',A=H.read('AttemptEnded',P,lure),
                B=math2(H,'LessEqual',H.read('CurrentLucidity',LUCIDITY,H.read('Lucidity',P,lure)),'0'))
e = H.branch(e,failed).find_then_pin()
middle = multiply(H,draw.find_output_pin('SizeY'),'.43')
e = H.do(e,'HUD.DrawRect',RectColor='(R=.015,G=.035,B=.06,A=.94)',ScreenX='24',
         ScreenY=middle,ScreenW=width,ScreenH='88').find_then_pin()
H.do(e,'HUD.DrawText',Text='Lucidity empty. Restarting the dive...',TextColor='(R=1,G=.9,B=.8,A=1)',
     ScreenX='42',ScreenY=add(H,middle,'25'),Scale='2')
compile_save(hud)

mode = blueprint('BP_FishingMode', unreal.GameModeBase)
L.compile_blueprint(mode)
defaults = unreal.get_default_object(mode.generated_class())
defaults.set_editor_property('default_pawn_class',pawn.generated_class())
defaults.set_editor_property('hud_class',hud.generated_class())
compile_save(mode)

def find_actor(label):
    return next((a for a in ACTORS.get_all_level_actors() if a.get_actor_label() == label),None)

check(LEVELS.load_level(MAP), 'load fishing')
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
world.get_world_settings().set_editor_property('default_game_mode',mode.generated_class())
completion = check(find_actor('BP_DreamCompletion'), 'existing Level 3 completion')
completion.set_editor_property('SaveSlot','DreamSeeker.Memory.03')
check(find_actor('BP_ReturnToMemoryHub'),'existing Level 3 early return')

# Depth, center, patrol amplitude, radians/s, phase, mesh, width, height.
rows = [
    (6250, -2800, 660, 1.08, .15, 'AngelFish', 315, 195),
    (5460, -3140, 570, 1.10, 2.2, 'ButterflyFish', 265, 195),
    (4980, -2200, 500, .9, .4, 'AngelFish', 330, 205),
    (4210, -2950, 780, 1.22, 1.8, 'ButterflyFish', 290, 210),
    (3570, -2200, 490, 1.3, 2.7, 'AngelFish', 330, 200),
    (3150, -3410, 490, 1.1, .9, 'ButterflyFish', 280, 195),
    (2460, -2730, 780, 1.24, 2.4, 'AngelFish', 355, 210),
    (1900, -3210, 510, 1.0, .7, 'ButterflyFish', 290, 205),
    (6720, -2530, 590, 1.18, 2.6, 'ButterflyFish', 265, 195),
    (5940, -3140, 580, 1.23, .4, 'AngelFish', 305, 190),
    (5200, -2590, 640, 1.19, 2.8, 'ButterflyFish', 270, 190),
    (4490, -2220, 520, 1.22, .6, 'AngelFish', 310, 200),
    (3880, -3220, 610, 1.27, 2.9, 'ButterflyFish', 280, 195),
    (2800, -2250, 570, 1.28, .8, 'AngelFish', 310, 195),
    (2170, -2520, 570, 1.18, 2.6, 'ButterflyFish', 275, 190),
    (1290, -2260, 0, 0, 0, 'ClownFish', 495, 255),
]
for index, (depth, center, amplitude, rate, phase, mesh, width, height) in enumerate(rows):
    target = mesh == 'ClownFish'
    if not target:
        width, height = width * .8, height * .8
    label = 'Fishing - Target Clownfish' if target else f'Fishing - Patrol {index+1:02}'
    position = unreal.Vector(center,PLANE,depth)
    a = find_actor(label) or check(ACTORS.spawn_actor_from_class(fish.generated_class(),position,
                                                               unreal.Rotator()),label)
    a.set_actor_label(label)
    a.set_actor_location(position,False,False)
    a.set_folder_path('Fishing Gameplay')
    for name,value in dict(LaneCenter=float(center),DepthZ=float(depth),PatrolWidth=float(amplitude),
                           PatrolRate=float(rate),Phase=float(phase),HookRadius=width*.48,
                           BodyHeight=height*.5,IsTarget=target).items():
        a.set_editor_property(name,value)
    mesh = check(A.load_asset('/Game/StylizedUnderwater/Meshes/Fish/'+mesh),label)
    visual = a.get_component_by_class(unreal.StaticMeshComponent)
    visual.set_static_mesh(mesh)
    box = mesh.get_bounding_box()
    scale = width/(box.max.x-box.min.x)
    a.set_actor_scale3d(unreal.Vector(scale,scale,height/(box.max.z-box.min.z)))
check(LEVELS.save_current_level(),'save Level 3')

check(LEVELS.load_level('/Game/Dreamhub_MemoryCauseway'),'load hub')
entrance = check(find_actor('Memory 3 entrance'),'Dream 3 entrance')
entrance.set_editor_property('DreamAvailable',True)
entrance.set_editor_property('Destination',A.load_asset(MAP))
check(find_actor('Dream 3 coming soon'),'Dream 3 placeholder').set_actor_hidden_in_game(True)
check(find_actor('Dream 3 completed beacon'),'Dream 3 beacon').set_actor_hidden_in_game(False)
for actor in ACTORS.get_all_level_actors():
    if isinstance(actor,unreal.TextRenderActor):
        caption = actor.text_render.get_editor_property('text')
        if str(caption) == 'TWO DREAMS TO EXPLORE. MORE MEMORIES TO COME.':
            actor.text_render.set_text('THREE DREAMS TO EXPLORE. MORE MEMORIES TO COME.')
check(LEVELS.save_current_level(),'save hub')
LEVELS.load_level(MAP)
unreal.log_warning('FISHING BUILD READY')







