import unreal,ast
from pathlib import Path
source=Path(__file__).with_name('build_race_gameplay.py').read_text();exec(source.split('racepath=')[0],globals())
E=unreal.MaterialEditingLibrary;ROOT='/Game/DreamSeeker/Levels/AgainstTheTide';ART=ROOT+'/Cinematic'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level(ROOT+'/LV_AgainstTheTide')
for a in actors.get_all_level_actors():
 label=a.get_actor_label()
 if label=='Soft blue water fill':a.get_component_by_class(unreal.DirectionalLightComponent).set_intensity(.4)
 if isinstance(a,unreal.PostProcessVolume):
  s=a.get_editor_property('settings');s.set_editor_property('auto_exposure_bias',-.15);a.set_editor_property('settings',s)
fill=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,-3000,1200),unreal.Rotator(0,-22,90));fill.set_actor_label('Warm light through open windows');c=fill.get_component_by_class(unreal.DirectionalLightComponent);c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_intensity(.75);c.set_light_color(unreal.LinearColor(1,.63,.38));c.set_cast_shadows(False)
for x in (-900,16200):
 a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x,-600,600));a.set_actor_label('End gallery stone wall');c=a.static_mesh_component;c.set_static_mesh(A.load_asset('/Engine/BasicShapes/Cube'));c.set_material(0,A.load_asset(ART+'/Materials/M_DuskPlaster'));c.set_collision_profile_name('NoCollision');a.set_actor_scale3d(unreal.Vector(1.5,34,24))
# Subtle light on the player preserves the readable swimming silhouette.
bp=A.load_asset(ROOT+'/BP_RaceSwimmer');light=component(bp,unreal.PointLightComponent,'SwimmerReadabilityLight');light.set_editor_property('relative_location',unreal.Vector(0,130,70));light.set_intensity(70);light.set_light_color(unreal.LinearColor(.6,.83,1));light.set_attenuation_radius(260);light.set_cast_shadows(False);compile_save(bp)
for name in ('M_WeatheredLimestone','M_DuskPlaster','M_DeepSlate'):
 m=A.load_asset(ART+'/Materials/'+name)
 for o in E.get_all_expressions_in_material(m) if hasattr(E,'get_all_expressions_in_material') else []:
  if isinstance(o,unreal.MaterialExpressionNoise):o.set_editor_property('output_min',.95);o.set_editor_property('output_max',1.02)
 E.recompile_material(m);A.save_loaded_asset(m,False)
# Reduce the visible shaft opacity rather than obscuring gameplay with bright planes.
m=A.load_asset(ART+'/Materials/M_SunsetHaze');o=E.get_material_property_input_node(m,unreal.MaterialProperty.MP_OPACITY);o.set_editor_property('r',.012);E.recompile_material(m);A.save_loaded_asset(m,False)
assert levels.save_current_level()
for case in ('Win','Loss','Empty','Render'):
 assert levels.load_level(ROOT+'/LV_AgainstTheTide')
 for a in actors.get_all_level_actors():
  if a.get_class().get_name()=='BP_DreamCompletion_C':a.set_editor_property('SaveSlot','DreamSeeker.QA.Race.'+case)
 actors.spawn_actor_from_class(A.load_blueprint_class('/Game/__RaceQA/BP_Test'+case),unreal.Vector())
 assert unreal.EditorLoadingAndSavingUtils.save_map(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),'/Game/__RaceQA/'+case)
