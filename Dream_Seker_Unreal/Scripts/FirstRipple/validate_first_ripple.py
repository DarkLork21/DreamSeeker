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
saved=Path(unreal.Paths.project_saved_dir());logs=saved/'Logs'
def log(name):return (logs/name).read_text()
rhythm=log('EasierRhythm.log');normal=log('BalanceNormalCurrent.log');sprint=log('BalanceSprintCurrent.log');death=log('FinalBalanceFailure.log');route=log('FinalSwimming.log')
def values(text):return [float(v) for v in re.findall(r'PersistentLevel.BP_RhythmSwimmer_C_0.Lucidity.CurrentLucidity = ([\d.]+)',text)]
rx=values(rhythm);nx=[float(v) for v in re.findall(r'CollisionCylinder.RelativeLocation = \(X=([\d.\-]+)',normal)]
sx=[float(v) for v in re.findall(r'CollisionCylinder.RelativeLocation = \(X=([\d.\-]+)',sprint)]
minimum=float(re.search(r'MinimumLucidity = ([\d.]+)',sprint).group(1));crossed=float(re.search(r'CrossedAt = ([\d.]+)',sprint).group(1))
report.update({'perfect_rhythm_lucidity':rx,'normal_current_final_x':nx[-1],'sprint_final_x':sx[-1],'sprint_crossed_at_seconds':crossed,'minimum_lucidity_during_sprint':minimum,
        'perfect_rhythm_restores':rx[0]==90 and rx[1]==90,'last_dream_recovery_switch':rx[2]==90,
        'normal_cannot_cross':nx[-1]<7600,'sprint_can_cross':sx[-1]>8600 and crossed>0 and minimum>0,
        'empty_bar_fails':'DreamFailed = True' in death,'restarts_same_dream':death.count('Load map complete /Game/__FirstRippleQA/BalanceFailure')>=2,
        'restart_refills':values(death).count(100)>=2,'whole_route_completes':'Load map complete /Game/Dreamhub_MemoryCauseway' in route,
        'no_access_errors':all('Accessed None' not in s for s in (rhythm,normal,sprint,death,route))})
report['passed']=all(report[k] for k in ('perfect_rhythm_restores','last_dream_recovery_switch','normal_cannot_cross','sprint_can_cross','empty_bar_fails','restarts_same_dream','restart_refills','whole_route_completes','no_access_errors'))
(saved/'LucidityBalanceValidation.json').write_text(json.dumps(report,indent=2));assert report['passed'],report

assert not report['missing_dependencies'] and not report['blueprint_errors']
unreal.log('FIRST_RIPPLE_VALIDATION '+json.dumps(report))
