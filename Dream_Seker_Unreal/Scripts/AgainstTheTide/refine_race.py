import unreal,ast
from pathlib import Path
source=Path(__file__).with_name('build_race_gameplay.py').read_text();exec(source.split('racepath=')[0],globals())
E=unreal.MaterialEditingLibrary;ROOT='/Game/DreamSeeker/Levels/AgainstTheTide';PC=ROOT+'/BP_RaceSwimmer.BP_RaceSwimmer_C'
pawn=A.load_asset(ROOT+'/BP_RaceSwimmer')
for h in sub.k2_gather_subobject_data_for_blueprint(pawn):
    o=data.get_object_for_blueprint(data.get_data(h),pawn)
    if isinstance(o,unreal.CameraComponent):
        o.set_editor_property('relative_location',unreal.Vector(300,2600,310));o.set_editor_property('relative_rotation',unreal.Rotator(0,-3,-90));o.set_editor_property('field_of_view',52)
compile_save(pawn)
# Require the player to be ahead of every opponent at the finish.
director=A.load_asset(ROOT+'/BP_RaceDirector');g=unreal.BlueprintGraphEditor.get_graph_editor(L.find_event_graph(director));G=Graph(g,22000)
win=next(n for n in g.list_all_nodes() if str(n.get_node_title()).replace(' ','')=='WinRace' and n.find_execute_pin().is_valid())
branch=win.find_execute_pin().list_connected_pins()[0].get_owning_node()
old=branch.find_input_pin('Condition').list_connected_pins()[0];branch.find_input_pin('Condition').break_pin_links()
p=G.read('Player');loc=G.call('Actor.K2_GetActorLocation');G.link(p,loc.find_self_pin());x=G.call('KismetMathLibrary.BreakVector',InVec=loc.find_output_pin('ReturnValue')).find_output_pin('X')
front=G.math('FMax',A=G.read('Rival1X'),B=G.math('FMax',A=G.read('Rival2X'),B=G.read('Rival3X')))
G.put(branch.find_input_pin('Condition'),G.math('BooleanAND',A=old,B=G.math('GreaterEqual_DoubleDouble',A=x,B=front)));compile_save(director)
# Restrained aqua tiling instead of high-contrast checkerboard.
def material(name,rgb):
    m=tools.create_asset(name,ROOT+'/Materials',unreal.Material,unreal.MaterialFactoryNew()) if not A.does_asset_exist(ROOT+'/Materials/'+name) else A.load_asset(ROOT+'/Materials/'+name)
    E.delete_all_material_expressions(m);c=E.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-200,0);c.set_editor_property('constant',unreal.LinearColor(*rgb,1));E.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR);E.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES);E.recompile_material(m);A.save_loaded_asset(m,False);return m
pale=material('M_PaleAquaTile',(.17,.29,.28));dark=material('M_MutedAquaTile',(.13,.24,.23))
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level(ROOT+'/LV_AgainstTheTide')
for a in actors.get_all_level_actors():
    name=a.get_actor_label()
    if name=='Front pool coping':a.set_actor_location(unreal.Vector(4200,510,-425),False,False)
    if name=='Sunset through the gallery':
        c=a.get_component_by_class(unreal.DirectionalLightComponent);c.set_intensity(1.3);c.set_light_color(unreal.LinearColor(1,.7,.48))
    if name=='Cool pool fill':a.get_component_by_class(unreal.SkyLightComponent).set_intensity(.55)
    if name.startswith('Pool detail batch'):
        c=a.get_component_by_class(unreal.InstancedStaticMeshComponent);m=c.get_material(0)
        if c.static_mesh.get_name()=='Cube' and m.get_name() in ('M_WarmStone','M_RoseTile'):c.set_material(0,pale if m.get_name()=='M_WarmStone' else dark)
    if name.startswith('Rival '):
        i=int(name[-1]);m=A.load_asset(ROOT+'/Materials/'+('M_CoralCap','M_IvoryCap','M_VioletCap')[i-1])
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if str(c.get_name()).startswith(('RaceCap','Body')):c.set_material(0,m)
assert levels.save_current_level()
# Refresh isolated maps after scene changes, preserving their test observer and slots.
for case in ('Win','Loss','Empty','Render'):
    assert levels.load_level(ROOT+'/LV_AgainstTheTide')
    for a in actors.get_all_level_actors():
        if a.get_class().get_name()=='BP_DreamCompletion_C':a.set_editor_property('SaveSlot','DreamSeeker.QA.Race.'+case)
    actors.spawn_actor_from_class(A.load_blueprint_class('/Game/__RaceQA/BP_Test'+case),unreal.Vector())
    assert unreal.EditorLoadingAndSavingUtils.save_map(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),'/Game/__RaceQA/'+case)
unreal.log('RACE_REFINED')
