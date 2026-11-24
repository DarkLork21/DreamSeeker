import unreal,ast
from pathlib import Path
source=Path(__file__).with_name('build_race_gameplay.py').read_text();exec(source.split('racepath=')[0],globals())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
PC=ROOT+'/BP_RaceSwimmer.BP_RaceSwimmer_C';MC=ROOT+'/BP_RaceDirector.BP_RaceDirector_C';LC='/Game/DreamSeeker/Blueprints/Components/BPC_Lucidity.BPC_Lucidity_C'
for case in ('Win','Loss','Empty','Render'):
    path='/Game/__RaceQA/BP_Test'+case
    bp=A.load_asset(path) if A.does_asset_exist(path) else tools.create_asset('BP_Test'+case,'/Game/__RaceQA',unreal.Blueprint,unreal.BlueprintFactory())
    if not bp:raise RuntimeError(path)
    for name,kind,default in (('NextKick','real',4.2),('LeftNext','bool',True)):
        variable(bp,name,kind,default)
    g=unreal.BlueprintGraphEditor.get_graph_editor(L.find_event_graph(bp));g.remove_nodes(g.list_all_nodes());G=Graph(g,0)
    begin=L.add_event_override(bp,'ReceiveBeginPlay',unreal.IntPoint());player=G.call('GameplayStatics.GetPlayerPawn').find_output_pin('ReturnValue');c,p=cast(G,begin.find_then_pin(),player,A.load_asset(ROOT+'/BP_RaceSwimmer'));e=G.set(c.find_then_pin(),'UseMouseSteering','false',PC,p);e=G.set(e,'AimDirection','1,0,0',PC,p)
    if case!='Empty':
        tick=L.add_event_override(bp,'ReceiveTick',unreal.IntPoint(0,7000));T=Graph(g,7500);now=T.call('GameplayStatics.GetTimeSeconds').find_output_pin('ReturnValue')
        pulse=T.branch(tick.find_then_pin(),T.math('GreaterEqual_DoubleDouble',A=now,B=T.read('NextKick')));e2=T.set(pulse.find_then_pin(),'NextKick',T.math('Add_DoubleDouble',A=now,B='.5'))
        if case in ('Win','Render'):
            # Repeat controlled sprint/recovery cycles across the longer course.
            age=T.math('Subtract_DoubleDouble',A=now,B='4')
            sprint=T.math('Greater_DoubleDouble',A=T.math('Sin',A=T.math('Multiply_DoubleDouble',A=age,B='.5711986643')),B='.05')
            e2=T.set(e2,'Sprinting',sprint,PC,p)
        side=T.branch(e2,T.read('LeftNext'))
        for left in (True,False):
            n=T.do(side.find_then_pin() if left else side.find_else_pin(),PC+(':KickLeft' if left else ':KickRight'));T.link(p,n.find_self_pin());T.set(n.find_then_pin(),'LeftNext',str(not left).lower())
    def command(s,delay=0):
        global e
        if delay:e=G.do(e,'KismetSystemLibrary.Delay',Duration=str(delay)).find_then_pin()
        e=G.do(e,'KismetSystemLibrary.ExecuteConsoleCommand',Command=s).find_then_pin()
    if case=='Empty':
        command('GetAll BPC_Lucidity_C CurrentLucidity',4.5);e=G.set(e,'CurrentLucidity','0',LC,G.read('Lucidity',PC,p));command('GetAll BP_RaceSwimmer_C DreamFailed',.3)
    elif case=='Render':
        out=Path(__file__).parent.parent/'outputs/DreamSeeker-Level2';out.mkdir(exist_ok=True)
        command('Shot showui -nosuffix filename="'+str(out/'Race-Start.png').replace('\\','/')+'"',2)
        command('Shot showui -nosuffix filename="'+str(out/'Race-In-Progress.png').replace('\\','/')+'"',9)
        command('Shot showui -nosuffix filename="'+str(out/'Race-Central-Gallery.png').replace('\\','/')+'"',12)
        command('Shot showui -nosuffix filename="'+str(out/'Race-Final-Stretch.png').replace('\\','/')+'"',12)
        command('Quit',.5)
    else:
        for j in range(12):
            command('GetAll BP_RaceDirector_C RaceTime',5);command('GetAll BP_RaceDirector_C RacePosition');command('GetAll BP_RaceDirector_C Finished');command('GetAll BP_RaceDirector_C PlayerWon');command('GetAll BPC_Lucidity_C CurrentLucidity');command('GetAll CapsuleComponent RelativeLocation')
    compile_save(bp)
    assert levels.load_level(ROOT+'/LV_AgainstTheTide')
    for a in actors.get_all_level_actors():
        if a.get_class().get_name()=='BP_DreamCompletion_C':a.set_editor_property('SaveSlot','DreamSeeker.QA.Race.'+case)
    actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector())
    assert unreal.EditorLoadingAndSavingUtils.save_map(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),'/Game/__RaceQA/'+case)
unreal.log('RACE_TESTS_READY')
