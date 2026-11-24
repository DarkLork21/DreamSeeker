import unreal
unreal.AssetRegistryHelpers.get_asset_registry().search_all_assets(True)
A=unreal.EditorAssetLibrary
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ROOT='/Game/DreamSeeker/Levels/AgainstTheTide'
assert levels.load_level(ROOT+'/LV_AgainstTheTide')
for a in actors.get_all_level_actors():
    label=a.get_actor_label()
    if isinstance(a,unreal.StaticMeshActor) and label in ('Dusk beyond the glass','Low remembered sun','Continuous moving pool surface','Water depth','Dark barrel-vault ceiling'):a.static_mesh_component.set_cast_shadow(False)
    if label.startswith('Cinematic detail batch'):
        c=a.get_component_by_class(unreal.InstancedStaticMeshComponent)
        if c.get_material(0).get_name() in ('M_QuietWindowGlass','M_SunsetHaze'):c.set_cast_shadow(False)
    if label=='Cool interior fill':
        c=a.get_component_by_class(unreal.SkyLightComponent);c.set_editor_property('real_time_capture',False)
        cube=A.load_asset('/Engine/MapTemplates/Sky/SunsetAmbientCubemap')
        if cube:
            c.set_editor_property('source_type',unreal.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP);c.set_editor_property('cubemap',cube)
        c.set_intensity(.55)
fill=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,2000,1000),unreal.Rotator(0,-32,-90));fill.set_actor_label('Soft blue water fill');c=fill.get_component_by_class(unreal.DirectionalLightComponent);c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_intensity(.55);c.set_light_color(unreal.LinearColor(.42,.65,1));c.set_cast_shadows(False)
assert levels.save_current_level()
# One short visual check of the actual start, after materials have warmed.
bp=A.load_blueprint_class('/Game/__RaceQA/BP_TestRender');actors.spawn_actor_from_class(bp,unreal.Vector())
assert unreal.EditorLoadingAndSavingUtils.save_map(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),'/Game/__RaceQA/Render')
