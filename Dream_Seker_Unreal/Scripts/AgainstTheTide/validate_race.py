import unreal,json
from pathlib import Path
A=unreal.EditorAssetLibrary;L=unreal.BlueprintEditorLibrary;ROOT='/Game/DreamSeeker/Levels/AgainstTheTide'
report={'blueprint_errors':[],'missing_dependencies':[]}
registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True)
for path in A.list_assets(ROOT,True,False):
    obj=A.load_asset(path);assert obj,path
    if isinstance(obj,unreal.Blueprint):
        L.compile_blueprint(obj)
        for raw in L.list_graphs(obj):
            if unreal.BlueprintGraphEditor.get_graph_editor(raw).list_nodes_with_errors():report['blueprint_errors'].append(path)
    for dep in registry.get_dependencies(path.split('.')[0],unreal.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True)):
        if str(dep).startswith('/Game/') and not A.does_asset_exist(str(dep)):report['missing_dependencies'].append(str(dep))
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level(ROOT+'/LV_AgainstTheTide');allactors=actors.get_all_level_actors();report['actors']=len(allactors)
director=next(a for a in allactors if a.get_class().get_name()=='BP_RaceDirector_C')
report['finish_x']=director.get_editor_property('FinishX')
report['three_rivals']=all(director.get_editor_property('Rival'+str(i)) for i in (1,2,3))
report['completion_slot']=next(a for a in allactors if a.get_class().get_name()=='BP_DreamCompletion_C').get_editor_property('SaveSlot')
report['original_team_map_preserved']=A.does_asset_exist('/Game/Level_2_Swimming')
assert levels.load_level('/Game/Dreamhub_MemoryCauseway')
entrance=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Memory 2 entrance')
report['cloud_destination']=str(entrance.get_editor_property('destination'))
report['five_saved_completion_beacons']=sum(a.get_class().get_name()=='BP_CloudCompletion_C' for a in actors.get_all_level_actors())==5
saved=Path(unreal.Paths.project_saved_dir());logs=saved/'Logs'
win=(logs/'LongRaceWin.log').read_text();loss=(logs/'LongRaceLoss.log').read_text();empty=(logs/'LongRaceEmpty.log').read_text();route=(logs/'RaceCloudRoute.log').read_text()
report['win_returns_to_hub']='Load map complete /Game/Dreamhub_MemoryCauseway' in win
report['win_saves_seal']=unreal.GameplayStatics.does_save_game_exist('DreamSeeker.QA.Race.Win',0)
report['loss_restarts_race']='Load map complete '+ROOT+'/LV_AgainstTheTide' in loss
report['loss_awards_no_seal']=not unreal.GameplayStatics.does_save_game_exist('DreamSeeker.QA.Race.Loss',0)
report['empty_restarts']='DreamFailed = True' in empty and empty.count('Load map complete /Game/__RaceQA/Empty')>=2
report['cloud_enters_race']='Load map complete '+ROOT+'/LV_AgainstTheTide' in route
report['no_runtime_access_errors']=all('Accessed None' not in s and 'Blueprint Runtime Error' not in s for s in (win,loss,empty,route))
report['long_course']=report['finish_x']==15000.0
report['passed']=report['long_course'] and all(report[k] for k in ('three_rivals','original_team_map_preserved','five_saved_completion_beacons','win_returns_to_hub','win_saves_seal','loss_restarts_race','loss_awards_no_seal','empty_restarts','cloud_enters_race','no_runtime_access_errors')) and report['completion_slot']=='DreamSeeker.Memory.02' and not report['blueprint_errors'] and not report['missing_dependencies']
(saved/'RaceValidation.json').write_text(json.dumps(report,indent=2));unreal.log('RACE_VALIDATION '+json.dumps(report));assert report['passed']
