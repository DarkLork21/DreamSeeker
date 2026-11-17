import unreal,ast,math,json
from pathlib import Path
source=Path(__file__).with_name('build_first_ripple_gameplay.py').read_text();tree=ast.parse(source);nodes=[]
for n in tree.body:
    if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='path' for t in n.targets):break
    nodes.append(n)
exec(compile(ast.Module(body=nodes,type_ignores=[]),'helpers','exec'),globals())
ROOT='/Game/DreamSeeker/DreamHub/MemoryCauseway'
factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.Actor)
path=ROOT+'/BP_CloudCompletion';bp=A.load_asset(path) if A.does_asset_exist(path) else unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_CloudCompletion',ROOT,unreal.Blueprint,factory)
L.add_member_variable(bp,'SaveSlot',L.get_basic_type_by_name('string'));L.set_blueprint_variable_instance_editable(bp,'SaveSlot',True)
L.add_member_variable(bp,'IsComplete',L.get_basic_type_by_name('bool'))
L.compile_blueprint(bp)
def component(kind,name):
    for h in sub.k2_gather_subobject_data_for_blueprint(bp):
        o=data.get_object_for_blueprint(data.get_data(h),bp)
        if o and o.get_name()==name:return o
    h,err=sub.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=sub.k2_gather_subobject_data_for_blueprint(bp)[0],new_class=kind,blueprint_context=bp));assert not str(err),err
    sub.rename_subobject(h,unreal.Text(name));return data.get_object_for_blueprint(data.get_data(h),bp)
lens=component(unreal.StaticMeshComponent,'CompletionStar');lens.set_static_mesh(A.load_asset('/Engine/BasicShapes/Sphere'));lens.set_material(0,A.load_asset(ROOT+'/Materials/M_LanternFlame'));lens.set_collision_profile_name('NoCollision');lens.set_editor_property('relative_scale3d',unreal.Vector(.28,.28,.28))
caption=component(unreal.TextRenderComponent,'CompletedCaption');caption.set_text('DREAM COMPLETE');caption.set_world_size(24);caption.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER);caption.set_text_render_color(unreal.Color(255,225,155,255));caption.set_editor_property('relative_location',unreal.Vector(0,0,-60));caption.set_editor_property('relative_rotation',unreal.Rotator(0,0,90))
g=unreal.BlueprintGraphEditor.get_graph_editor(L.find_event_graph(bp));g.remove_nodes(g.list_all_nodes());G=Graph(g,0)
b=L.add_event_override(bp,'ReceiveBeginPlay',unreal.IntPoint(0,0));e=G.do(b.find_then_pin(),'GameplayStatics.DoesSaveGameExist',SlotName=G.read('SaveSlot'))
done=G.set(e.find_then_pin(),'IsComplete',e.find_output_pin('ReturnValue'))
for name in ('CompletionStar','CompletedCaption'):
    n=G.do(done,'SceneComponent.SetVisibility',bNewVisibility=G.read('IsComplete'),bPropagateToChildren='true');G.link(G.read(name),n.find_self_pin());done=n.find_then_pin()
compile_save(bp)
# Repair the older ending seals' impure save lookup if needed.
lock=A.load_asset(ROOT+'/BP_DreamLockLight');g=unreal.BlueprintGraphEditor.get_graph_editor(L.find_event_graph(lock))
exists=next(n for n in g.list_all_nodes() if str(n.get_node_title()).replace(' ','')=='DoesSaveGameExist')
if not exists.find_execute_pin().list_connected_pins():
    begin=next(n for n in g.list_all_nodes() if 'BeginPlay' in str(n.get_node_title()).replace(' ',''));old=begin.find_then_pin().list_connected_pins()[0];begin.find_then_pin().break_pin_links();assert begin.find_then_pin().try_create_connection(exists.find_execute_pin());assert exists.find_then_pin().try_create_connection(old)
compile_save(lock)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level('/Game/Dreamhub_MemoryCauseway')
for a in actors.get_all_level_actors():
    if a.get_class()==bp.generated_class():actors.destroy_actor(a)
for i,x in enumerate((-1740,-770,250,1270,2280),1):
    z=.065*(x+2700)+22*math.sin((x+2700)/520)
    a=actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector(x,80,z+585));a.set_actor_label('Dream '+str(i)+' completed beacon');a.set_editor_property('SaveSlot',f'DreamSeeker.Memory.{i:02d}')
assert levels.save_current_level()
unreal.log('CLOUD_COMPLETION_READY')
