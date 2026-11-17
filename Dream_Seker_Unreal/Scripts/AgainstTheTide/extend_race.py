import unreal,ast
from pathlib import Path
source=Path(__file__).with_name('build_race_gameplay.py').read_text();exec(source.split('racepath=')[0],globals())
ROOT='/Game/DreamSeeker/Levels/AgainstTheTide'
bp=A.load_asset(ROOT+'/BP_RaceSwimmer');g=unreal.BlueprintGraphEditor.get_graph_editor(L.find_event_graph(bp));removed=0
for n in list(g.list_all_nodes()):
    pins={str(p.get_pin_name()):p for p in n.list_input_pins()}
    if 'Max' in pins and not pins['Max'].list_connected_pins():
        try:
            if float(pins['Max'].get_pin_value())==10850:assert pins['Max'].set_pin_value('15500')
        except (ValueError,TypeError):pass
    # The race director owns victory; the inherited first-dream objective must never travel.
    if str(n.get_node_title()).replace(' ','')=='CompleteDream':g.remove_nodes([n]);removed+=1
compile_save(bp)
bp=A.load_asset(ROOT+'/BP_RaceDirector');g=unreal.BlueprintGraphEditor.get_graph_editor(L.find_event_graph(bp))
for n in g.list_all_nodes():
    pins={str(p.get_pin_name()):p for p in n.list_input_pins()}
    if 'Greater' in str(n.get_node_title()) or str(n.get_node_title()).replace(' ','')=='float>float':
        if 'B' in pins and not pins['B'].list_connected_pins():
            try:
                value=float(pins['B'].get_pin_value())
                if value in (10,16):assert pins['B'].set_pin_value('18' if value==10 else '30')
            except (ValueError,TypeError):pass
unreal.get_default_object(bp.generated_class()).set_editor_property('FinishX',15000.0);compile_save(bp)
hud=A.load_asset(ROOT+'/BP_RaceHUD')
for raw in L.list_graphs(hud):
    for n in unreal.BlueprintGraphEditor.get_graph_editor(raw).list_all_nodes():
        for p in n.list_input_pins():
            value=p.get_pin_value()
            if value in ('7650','7650.000000'):assert p.set_pin_value('14650')
            if str(p.get_pin_name())=='B' and not p.list_connected_pins():
                try:
                    v=float(value)
                    if v in (7,16,21):assert p.set_pin_value({7:'9',16:'20',21:'32'}[v])
                except (ValueError,TypeError):pass
compile_save(hud)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level(ROOT+'/LV_AgainstTheTide')
for a in actors.get_all_level_actors():
    if a.get_class().get_name()=='BP_RaceDirector_C':a.set_editor_property('FinishX',15000.0)
assert levels.save_current_level()
unreal.log('LONG_RACE_READY removed_inherited_objectives='+str(removed))
