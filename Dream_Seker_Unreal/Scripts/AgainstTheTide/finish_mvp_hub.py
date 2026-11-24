import unreal,ast,math
from pathlib import Path
source=Path(__file__).with_name('build_race_gameplay.py').read_text();exec(source.split('racepath=')[0],globals())
ROOT='/Game/DreamSeeker/DreamHub/MemoryCauseway'
f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor)
bp=A.load_asset(ROOT+'/BP_MVPCompletion') if A.does_asset_exist(ROOT+'/BP_MVPCompletion') else tools.create_asset('BP_MVPCompletion',ROOT,unreal.Blueprint,f)
for name,label,z,size in (('Title','MVP COMPLETE',0,30),('Thanks','THANK YOU FOR PLAYING',-50,23),('Future','MORE DREAMS COMING SOON',-90,19)):
 c=component(bp,unreal.TextRenderComponent,name);c.set_text(label);c.set_world_size(size);c.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER);c.set_text_material(A.load_asset(ROOT+'/Materials/M_LegibleMemoryText'));c.set_text_render_color(unreal.Color(245,220,165));c.set_editor_property('relative_location',unreal.Vector(0,0,z));c.set_editor_property('relative_rotation',unreal.Rotator(0,0,90))
g=unreal.BlueprintGraphEditor.get_graph_editor(L.find_event_graph(bp));g.remove_nodes(g.list_all_nodes());G=Graph(g,0)
begin=L.add_event_override(bp,'ReceiveBeginPlay',unreal.IntPoint());one=G.do(begin.find_then_pin(),'GameplayStatics.DoesSaveGameExist',SlotName='DreamSeeker.Memory.01');two=G.do(one.find_then_pin(),'GameplayStatics.DoesSaveGameExist',SlotName='DreamSeeker.Memory.02');both=G.math('BooleanAND',A=one.find_output_pin('ReturnValue'),B=two.find_output_pin('ReturnValue'));e=two.find_then_pin()
for name in ('Title','Thanks','Future'):
 n=G.do(e,'SceneComponent.SetVisibility',bNewVisibility=both);G.link(G.read(name),n.find_self_pin());e=n.find_then_pin()
compile_save(bp)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level('/Game/Dreamhub_MemoryCauseway')
if not any(a.get_class().get_name()=='BP_MVPCompletion_C' for a in actors.get_all_level_actors()):
 x=2890;z=.065*(x+2700)+22*math.sin((x+2700)/520)
 a=actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector(x,110,z+590));a.set_actor_label('Two-dream MVP completion acknowledgement')
assert levels.save_current_level()
