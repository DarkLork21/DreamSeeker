import unreal,json,re
from pathlib import Path
A=unreal.EditorAssetLibrary;L=unreal.BlueprintEditorLibrary
root='/Game/DreamSeeker/Levels/FirstRipple';swim='/Game/DreamSeeker/Swimming'
registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True)
report={'missing_dependencies':[],'blueprint_errors':[]}
for base in (root,swim):
    for path in A.list_assets(base,True,False):
        obj=A.load_asset(path);assert obj,path
        if isinstance(obj,unreal.Blueprint):
            L.compile_blueprint(obj)
            for raw in L.list_graphs(obj):
                if unreal.BlueprintGraphEditor.get_graph_editor(raw).list_nodes_with_errors():report['blueprint_errors'].append(path)
        package=path.split('.')[0]
        for dep in registry.get_dependencies(package,unreal.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True)):
            if str(dep).startswith('/Game/') and not A.does_asset_exist(str(dep)):report['missing_dependencies'].append(str(dep))
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level(root+'/LV_FirstRipple')
allactors=actors.get_all_level_actors()
report['actors']=len(allactors)
report['has_home']=any(a.get_actor_label()=='Home timber walls' for a in allactors)
report['has_dive_obstacle']=any(a.get_actor_label()=='Fallen willow - dive beneath' and a.static_mesh_component.get_collision_enabled()!=unreal.CollisionEnabled.NO_COLLISION for a in allactors)
completion=next(a for a in allactors if a.get_class().get_name()=='BP_DreamCompletion_C')
report['completion_slot']=completion.get_editor_property('SaveSlot')
report['original_level_loads']=bool(A.load_asset('/Game/Level_1_Learning'))
report['uses_team_lucidity']=A.does_asset_exist('/Game/DreamSeeker/Blueprints/Components/BPC_Lucidity')
log=Path(unreal.Paths.project_saved_dir(),'Logs/FirstRippleFullRouteQA.log').read_text()
report['full_route_returns_to_hub']='Load map complete /Game/Dreamhub_MemoryCauseway' in log
report['same_side_no_recovery']='CurrentLucidity = 50.000000' in log and 'GoodStreak = 0.000000' in log
report['rhythm_restores']='CurrentLucidity = 57.500000' in log
report['sprint_consumes']='CurrentLucidity = 48.350000' in log
report['early_completion_blocked']='CompletedCrossing = False' in log
report['dive_visited']='VisitedDive = True' in log
positions=[float(v) for v in re.findall(r'CollisionCylinder.RelativeLocation = \(X=([\d.\-]+)',log)]
values=[float(v) for v in re.findall(r'PersistentLevel.BP_RhythmSwimmer_C_0.Lucidity.CurrentLucidity = ([\d.]+)',log)]
report['zero_lucidity_swims']='CurrentLucidity = 0.000000' in log and len(positions)>1 and positions[1]>positions[0]
report['last_dream_recovery_switch']=len(values)>2 and values[1]==values[2]
report['runtime_access_errors']='Accessed None' in log
report['passed']=not report['missing_dependencies'] and not report['blueprint_errors'] and report['has_home'] and report['has_dive_obstacle'] and report['completion_slot']=='DreamSeeker.Memory.01' and report['full_route_returns_to_hub'] and report['rhythm_restores'] and report['sprint_consumes'] and report['early_completion_blocked'] and not report['runtime_access_errors']
Path(unreal.Paths.project_saved_dir(),'FirstRippleValidation.json').write_text(json.dumps(report,indent=2))
unreal.log('FIRST_RIPPLE_VALIDATION '+json.dumps(report));assert report['passed']
