import unreal,ast
from pathlib import Path
source=Path(__file__).with_name('build_race_gameplay.py').read_text();exec(source.split('racepath=')[0],globals())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);LC='/Game/DreamSeeker/Blueprints/Components/BPC_Lucidity.BPC_Lucidity_C'
for case,pc,mapname in (('Lesson','/Game/DreamSeeker/Swimming/BP_RhythmSwimmer.BP_RhythmSwimmer_C','/Game/DreamSeeker/Levels/FirstRipple/LV_FirstRipple'),('Race',ROOT+'/BP_RaceSwimmer.BP_RaceSwimmer_C',ROOT+'/LV_AgainstTheTide')):
 name='BP_Generous'+case;path='/Game/__RaceQA/'+name
 f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor)
 bp=A.load_asset(path) if A.does_asset_exist(path) else tools.create_asset(name,'/Game/__RaceQA',unreal.Blueprint,f)
 g=unreal.BlueprintGraphEditor.get_graph_editor(L.find_event_graph(bp));g.remove_nodes(g.list_all_nodes());G=Graph(g,0)
 begin=L.add_event_override(bp,'ReceiveBeginPlay',unreal.IntPoint());c,p=cast(G,begin.find_then_pin(),G.call('GameplayStatics.GetPlayerPawn').find_output_pin('ReturnValue'),A.load_asset(pc.split('.')[0]));e=G.set(c.find_then_pin(),'UseMouseSteering','false',pc,p);e=G.set(e,'AimDirection','1,0,0',pc,p);health=G.read('Lucidity',pc,p);e=G.set(e,'CurrentLucidity','25',LC,health)
 def cmd(s,delay=0):
  global e
  if delay:e=G.do(e,'KismetSystemLibrary.Delay',Duration=str(delay)).find_then_pin()
  e=G.do(e,'KismetSystemLibrary.ExecuteConsoleCommand',Command=s).find_then_pin()
 for i,delay in enumerate((.25,.85,.35,1.05,.45,.70)):cmd('ke * '+('KickLeft' if i%2==0 else 'KickRight'),delay)
 cmd('GetAll BPC_Lucidity_C CurrentLucidity')
 for i in range(5):cmd('ke * KickRight',.4)
 cmd('GetAll BPC_Lucidity_C CurrentLucidity')
 e=G.set(e,'AllowRhythmRecovery','false',pc,p)
 for i in range(4):cmd('ke * '+('KickLeft' if i%2==0 else 'KickRight'),.5)
 cmd('GetAll BPC_Lucidity_C CurrentLucidity')
 compile_save(bp);assert levels.load_level(mapname)
 for a in actors.get_all_level_actors():
  if a.get_class().get_name()=='BP_DreamCompletion_C':a.set_editor_property('SaveSlot','DreamSeeker.QA.Generous.'+case)
 actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector())
 assert unreal.EditorLoadingAndSavingUtils.save_map(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),'/Game/__RaceQA/Generous'+case)
