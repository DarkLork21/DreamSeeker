import unreal,ast
from pathlib import Path
source=Path(__file__).with_name('build_first_ripple_gameplay.py').read_text();tree=ast.parse(source);nodes=[]
for n in tree.body:
    if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='path' for t in n.targets):break
    nodes.append(n)
exec(compile(ast.Module(body=nodes,type_ignores=[]),'swim_helpers','exec'),globals())
ROOT='/Game/DreamSeeker/Levels/FirstRipple';edit=unreal.MaterialEditingLibrary
sky=A.load_asset(ROOT+'/Materials/M_DuskSky');sky.set_editor_property('is_sky',True);edit.recompile_material(sky);assert A.save_loaded_asset(sky,False)
glow=A.load_asset(ROOT+'/Materials/M_LanternGold')
# Tone down the actual emissive input, retaining readable lanterns without washing out home.
node=edit.get_material_property_input_node(glow,unreal.MaterialProperty.MP_EMISSIVE_COLOR);node.set_editor_property('constant',unreal.LinearColor(.65,.34,.10,1));edit.recompile_material(glow);assert A.save_loaded_asset(glow,False)
# Fine noise creates timber and silt variation using native material expressions.
for name in ('M_HomeTimber','M_SunBleachedWood','M_Silt','M_WillowBark'):
    m=A.load_asset(ROOT+'/Materials/'+name);base=edit.get_material_property_input_node(m,unreal.MaterialProperty.MP_BASE_COLOR)
    noise=edit.create_material_expression(m,unreal.MaterialExpressionNoise,-750,180);noise.set_editor_property('scale',.035);noise.set_editor_property('levels',2);noise.set_editor_property('output_min',.55);noise.set_editor_property('output_max',1.0)
    mul=edit.create_material_expression(m,unreal.MaterialExpressionMultiply,-100,80);assert edit.connect_material_expressions(base,'',mul,'A');assert edit.connect_material_expressions(noise,'',mul,'B');assert edit.connect_material_property(mul,'',unreal.MaterialProperty.MP_BASE_COLOR)
    edit.recompile_material(m);assert A.save_loaded_asset(m,False)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level(ROOT+'/LV_FirstRipple')
green=A.load_asset(ROOT+'/Materials/M_ReedGreen')
for a in actors.get_all_level_actors():
    name=a.get_actor_label()
    if name.startswith('Water grass'):
        a.static_mesh_component.set_material(0,green);a.set_actor_scale3d(unreal.Vector(.65,.65,1.0))
    if isinstance(a,unreal.PointLight):a.get_component_by_class(unreal.PointLightComponent).set_intensity(180)
    if name=='Visible riverbed':a.set_actor_scale3d(unreal.Vector(120,40,3));a.set_actor_location(unreal.Vector(5500,-200,-625),False,False)
    if name=='Home stone foundation':a.set_actor_scale3d(unreal.Vector(13,9,1.0))
    if name=='Late afternoon sunlight':a.get_component_by_class(unreal.DirectionalLightComponent).set_intensity(2.0)
assert levels.save_current_level()

bp=A.load_asset('/Game/DreamSeeker/Swimming/BP_RhythmSwimmer')
g=unreal.BlueprintGraphEditor.get_graph_editor(L.find_event_graph(bp));G=Graph(g,14000)
# Require the final landing near the surface, after the dive.
setter=next(n for n in g.list_all_nodes() if str(n.get_node_title()).replace(' ','')=='SetCompletedCrossing')
win=setter.find_execute_pin().list_connected_pins()[0].get_owning_node()
previous=win.find_input_pin('Condition').list_connected_pins()[0];win.find_input_pin('Condition').break_pin_links()
location=G.call('Actor.K2_GetActorLocation').find_output_pin('ReturnValue');xyz=G.call('KismetMathLibrary.BreakVector',InVec=location)
G.put(win.find_input_pin('Condition'),G.math('BooleanAND',A=previous,B=G.math('Greater_DoubleDouble',A=xyz.find_output_pin('Z'),B='-120')))
# Remove the inherited magical wisp dust from Naia's swimming proxy.
for h in sub.k2_gather_subobject_data_for_blueprint(bp):
    obj=data.get_object_for_blueprint(data.get_data(h),bp)
    if isinstance(obj,unreal.NiagaraComponent):obj.set_editor_property('auto_activate',False)
    if isinstance(obj,unreal.CameraComponent):obj.set_editor_property('ortho_width',3000)
    if isinstance(obj,unreal.StaticMeshComponent) and str(obj.get_name()).startswith('Naia'):
        obj.set_editor_property('relative_scale3d',obj.get_editor_property('relative_scale3d')*1.25)
compile_save(bp)
unreal.log('FIRST_RIPPLE_POLISHED')
