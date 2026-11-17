"""Generous swimming recovery and an explicit two-dream MVP boundary."""
import unreal,ast,math
from pathlib import Path
source=Path(__file__).with_name('build_first_ripple_gameplay.py').read_text();tree=ast.parse(source);nodes=[]
for n in tree.body:
    if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='path' for t in n.targets):break
    nodes.append(n)
exec(compile(ast.Module(body=nodes,type_ignores=[]),'helpers','exec'),globals())
ROOT='/Game/DreamSeeker/DreamHub/MemoryCauseway'
for path in ('/Game/DreamSeeker/Swimming/BP_RhythmSwimmer','/Game/DreamSeeker/Levels/AgainstTheTide/BP_RaceSwimmer'):
 bp=A.load_asset(path)
 for raw in L.list_graphs(bp):
  if raw.get_name() not in ('KickLeft','KickRight'):continue
  for n in unreal.BlueprintGraphEditor.get_graph_editor(raw).list_all_nodes():
   pins={str(p.get_pin_name()):p for p in n.list_input_pins()}
   if 'InclusiveMin' in pins and 'Min' in pins:
    assert pins['Min'].set_pin_value('.18');assert pins['Max'].set_pin_value('1.25')
   if str(n.get_node_title()).replace(' ','')=='RestoreLucidity':assert pins['Amount'].set_pin_value('8.0')
 compile_save(bp)
for path in ('/Game/DreamSeeker/Swimming/BP_SwimGuideHUD','/Game/DreamSeeker/Levels/AgainstTheTide/BP_RaceHUD'):
 bp=A.load_asset(path)
 for raw in L.list_graphs(bp):
  for n in unreal.BlueprintGraphEditor.get_graph_editor(raw).list_all_nodes():
   for p in n.list_input_pins():
    v=p.get_pin_value()
    if v:
     new=v.replace('PERFECT RHYTHM','STEADY KICKS').replace('Perfect A / D rhythm','Alternating A / D kicks').replace('perfect rhythm','steady kicks').replace('Perfect rhythm','Steady kicks')
     if new!=v:assert p.set_pin_value(new)
 compile_save(bp)
bp=A.load_asset(ROOT+'/BP_ChooseMemory')
added=L.add_member_variable(bp,'DreamAvailable',L.get_basic_type_by_name('bool'));L.set_blueprint_variable_instance_editable(bp,'DreamAvailable',True);L.compile_blueprint(bp);unreal.get_default_object(bp.generated_class()).set_editor_property('DreamAvailable',True)
g=unreal.BlueprintGraphEditor.get_graph_editor(L.find_event_graph(bp));G=Graph(g,12000)
if added:
 travel=next(n for n in g.list_all_nodes() if 'OpenLevel' in str(n.get_node_title()).replace(' ',''));old=travel.find_execute_pin().list_connected_pins()[0];travel.find_execute_pin().break_pin_links();guard=G.branch(old,G.read('DreamAvailable'));G.link(guard.find_then_pin(),travel.find_execute_pin())
compile_save(bp)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level('/Game/Dreamhub_MemoryCauseway')
for a in actors.get_all_level_actors():
 label=a.get_actor_label()
 if label.startswith('Memory ') and label.endswith(' entrance'):
  number=int(label.split()[1]);a.set_editor_property('DreamAvailable',number<=2)
 if a.get_class().get_name()=='BP_CloudCompletion_C' and a.get_editor_property('SaveSlot') in ('DreamSeeker.Memory.03','DreamSeeker.Memory.04','DreamSeeker.Memory.05'):a.set_actor_hidden_in_game(True)
 if isinstance(a,unreal.TextRenderActor):
  value=str(a.text_render.get_editor_property('text'))
  if 'FIVE DREAMS' in value:a.text_render.set_text('TWO DREAMS TO EXPLORE. MORE MEMORIES TO COME.')
for i,x in ((3,250),(4,1270),(5,2280)):
 label=f'Dream {i} coming soon'
 if any(a.get_actor_label()==label for a in actors.get_all_level_actors()):continue
 z=.065*(x+2700)+22*math.sin((x+2700)/520)
 a=actors.spawn_actor_from_class(unreal.TextRenderActor,unreal.Vector(x,80,z+510),unreal.Rotator(0,0,90));a.set_actor_label(label);c=a.text_render;c.set_text('COMING SOON');c.set_world_size(32);c.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER);c.set_text_render_color(unreal.Color(210,220,240));c.set_text_material(A.load_asset(ROOT+'/Materials/M_LegibleMemoryText'))
assert levels.save_current_level()
unreal.log('MVP_READY two_dreams timing=.18-1.25 recovery=8')
