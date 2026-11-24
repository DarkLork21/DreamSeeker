import unreal,ast
from pathlib import Path
source=Path(__file__).with_name('build_first_ripple_gameplay.py').read_text();tree=ast.parse(source);nodes=[]
for n in tree.body:
    if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='path' for t in n.targets):break
    nodes.append(n)
exec(compile(ast.Module(body=nodes,type_ignores=[]),'swim_helpers','exec'),globals())
bp=A.load_asset('/Game/DreamSeeker/Swimming/BP_RhythmSwimmer');root=sub.k2_gather_subobject_data_for_blueprint(bp)[0]
h,error=sub.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root,new_class=unreal.TextRenderComponent,blueprint_context=bp));assert not str(error)
sub.rename_subobject(h,unreal.Text('KickRhythmCue'));cue=data.get_object_for_blueprint(data.get_data(h),bp)
cue.set_text('A  /  D');cue.set_world_size(25);cue.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER);cue.set_text_material(A.load_asset(HUB+'/Materials/M_LegibleMemoryText'));cue.set_text_render_color(unreal.Color(215,220,199,255));cue.set_editor_property('relative_location',unreal.Vector(0,100,110));cue.set_editor_property('relative_rotation',unreal.Rotator(0,0,90))
L.compile_blueprint(bp)
for name,is_left in (('KickLeft',True),('KickRight',False)):
    raw=next(r for r in L.list_graphs(bp) if r.get_name()==name);g=unreal.BlueprintGraphEditor.get_graph_editor(raw);G=Graph(g,1700)
    # Invalid or repeated kicks cannot be spammed to obtain full propulsion.
    power_set=next(n for n in g.list_all_nodes() if str(n.get_node_title()).replace(' ','')=='SetStrokePower')
    select=next(n for n in g.list_all_nodes() if n.find_input_pin('bPickA').is_valid() and float(n.find_input_pin('A').get_pin_value() or 0)==.6)
    select.find_input_pin('B').set_pin_value('0.0')
    old=select.find_input_pin('bPickA').list_connected_pins()[0];select.find_input_pin('bPickA').break_pin_links()
    first=G.math('Less_DoubleDouble',A=G.read('LastKickTime'),B='0')
    G.put(select.find_input_pin('bPickA'),G.math('BooleanOR',A=first,B=old))
    entry=g.find_graph_entry_pin();entry.break_pin_links()
    settext=G.do(entry,'TextRenderComponent.K2_SetText',Value=G.call('KismetTextLibrary.Conv_StringToText',InString='A  >  D' if is_left else 'D  >  A').find_output_pin('ReturnValue'))
    G.link(G.read('KickRhythmCue'),settext.find_self_pin())
    # An actual kick changes the matching leg pose, giving left/right input visible feedback.
    rotate=G.do(settext.find_then_pin(),'SceneComponent.K2_SetRelativeRotation',NewRotation='0,35,0' if is_left else '0,-15,0')
    G.link(G.read('Naia left leg' if is_left else 'Naia right leg'),rotate.find_self_pin())
    G.link(rotate.find_then_pin(),power_set.find_execute_pin())
compile_save(bp)
unreal.log('SWIM_FEEDBACK_FINISHED')
