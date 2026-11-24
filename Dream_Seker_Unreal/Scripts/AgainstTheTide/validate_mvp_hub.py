import unreal,json
from pathlib import Path
A=unreal.EditorAssetLibrary;L=unreal.BlueprintEditorLibrary
ROOT='/Game/DreamSeeker/DreamHub/MemoryCauseway'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level('/Game/Dreamhub_MemoryCauseway')
report={}
for a in actors.get_all_level_actors():
 if a.get_class().get_name()=='BP_ChooseMemory_C':report[a.get_actor_label()]=a.get_editor_property('DreamAvailable')
assert [report['Memory '+str(i)+' entrance'] for i in range(1,6)]==[True,True,False,False,False],report
report['coming_soon_labels']=sum(a.get_actor_label().endswith('coming soon') for a in actors.get_all_level_actors())
assert report['coming_soon_labels']==3
report['mvp_completion_acknowledgement']=any(a.get_class().get_name()=='BP_MVPCompletion_C' for a in actors.get_all_level_actors());assert report['mvp_completion_acknowledgement']
Path(unreal.Paths.project_saved_dir(),'MVPHubValidation.json').write_text(json.dumps(report,indent=2));unreal.log('MVP_HUB_VALIDATED '+json.dumps(report))
