import unreal,ast
from pathlib import Path
source=Path(__file__).with_name('build_first_ripple_gameplay.py').read_text();tree=ast.parse(source);nodes=[]
for n in tree.body:
    if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='path' for t in n.targets):break
    nodes.append(n)
exec(compile(ast.Module(body=nodes,type_ignores=[]),'swim_helpers','exec'),globals())
CLASS='/Game/DreamSeeker/Swimming/BP_RhythmSwimmer.BP_RhythmSwimmer_C';LC='/Game/DreamSeeker/Blueprints/Components/BPC_Lucidity.BPC_Lucidity_C'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
for case in ('Rhythm','NormalCurrent','SprintCurrent','Failure'):
    factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.Actor)
    name='BP_Balance'+case;path='/Game/__FirstRippleQA/'+name
    bp=A.load_asset(path) if A.does_asset_exist(path) else unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,'/Game/__FirstRippleQA',unreal.Blueprint,factory)
    g=unreal.BlueprintGraphEditor.get_graph_editor(L.find_event_graph(bp));g.remove_nodes(g.list_all_nodes());G=Graph(g,0)
    if case=='SprintCurrent':
        L.add_member_variable(bp,'MinimumLucidity',L.get_basic_type_by_name('real'));L.add_member_variable(bp,'CrossedAt',L.get_basic_type_by_name('real'));L.compile_blueprint(bp)
        cdo=unreal.get_default_object(bp.generated_class());cdo.set_editor_property('MinimumLucidity',100.0);cdo.set_editor_property('CrossedAt',-1.0)
    begin=L.add_event_override(bp,'ReceiveBeginPlay',unreal.IntPoint(0,0));player=G.call('GameplayStatics.GetPlayerPawn').find_output_pin('ReturnValue')
    c=g.create_node_from_name('Utilities|Casting|CastToActor',unreal.Vector2D(300,0),[]);assert g.retarget_node_class(c,unreal.Actor.static_class(),A.load_blueprint_class('/Game/DreamSeeker/Swimming/BP_RhythmSwimmer'));G.link(begin.find_then_pin(),c.find_execute_pin());G.link(player,c.find_input_pin('Object'));p=next(pin for pin in c.list_output_pins() if str(pin.get_pin_name()).startswith('As'))
    component=G.read('Lucidity',CLASS,p);e=G.set(c.find_then_pin(),'UseMouseSteering','false',CLASS,p);e=G.set(e,'AimDirection','1,0,0',CLASS,p)
    def setprop(name,value):
        global e
        e=G.set(e,name,value,LC if name=='CurrentLucidity' else CLASS,component if name=='CurrentLucidity' else p)
    def command(text,delay=0):
        global e
        if delay:e=G.do(e,'KismetSystemLibrary.Delay',Duration=str(delay)).find_then_pin()
        e=G.do(e,'KismetSystemLibrary.ExecuteConsoleCommand',Command=text).find_then_pin()
    def state():
        command('GetAll BPC_Lucidity_C CurrentLucidity');command('GetAll CapsuleComponent RelativeLocation');command('GetAll BP_RhythmSwimmer_C DreamFailed')
    if case=='Rhythm':
        setprop('CurrentLucidity','50')
        for i in range(9):command('ke * '+('KickLeft' if i%2==0 else 'KickRight'),.5)
        state()
        for i in range(8):command('ke * '+('KickRight' if i%2==0 else 'KickLeft'),.2)
        state()
        setprop('AllowRhythmRecovery','false')
        for i in range(8):command('ke * '+('KickRight' if i%2==0 else 'KickLeft'),.5)
        state()
    elif case in ('NormalCurrent','SprintCurrent'):
        setprop('Sprinting','true' if case=='SprintCurrent' else 'false')
        for i in range(22):command('ke * '+('KickLeft' if i%2==0 else 'KickRight'),.5)
        state()
        if case=='SprintCurrent':
            command('GetAll '+name+'_C MinimumLucidity');command('GetAll '+name+'_C CrossedAt')
            tick=L.add_event_override(bp,'ReceiveTick',unreal.IntPoint(0,10000));T=Graph(g,10300)
            e2=T.set(tick.find_then_pin(),'MinimumLucidity',T.math('FMin',A=T.read('MinimumLucidity'),B=T.read('CurrentLucidity',LC,component)))
            loc=T.call('Actor.K2_GetActorLocation');T.link(p,loc.find_self_pin());x=T.call('KismetMathLibrary.BreakVector',InVec=loc.find_output_pin('ReturnValue')).find_output_pin('X')
            done=T.branch(e2,T.math('BooleanAND',A=T.math('Greater_DoubleDouble',A=x,B='8650'),B=T.math('Less_DoubleDouble',A=T.read('CrossedAt'),B='0')))
            e2=T.set(done.find_then_pin(),'CrossedAt',T.call('GameplayStatics.GetTimeSeconds').find_output_pin('ReturnValue'))
            T.set(e2,'Sprinting','false',CLASS,p)
    else:
        state();command('GetAll BP_RhythmSwimmer_C StrokePower',.4);setprop('CurrentLucidity','0');state()
        command('GetAll BP_RhythmSwimmer_C DreamFailed',.3)
    compile_save(bp)
    assert levels.load_level('/Game/DreamSeeker/Levels/FirstRipple/LV_FirstRipple')
    for a in actors.get_all_level_actors():
        if isinstance(a,unreal.PlayerStart):a.set_actor_location(unreal.Vector(7390 if case.endswith('Current') else 250,0,-60),False,False)
        if a.get_class().get_name()=='BP_DreamCompletion_C':a.set_editor_property('SaveSlot','DreamSeeker.QA.Balance.'+case)
    actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector())
    assert unreal.EditorLoadingAndSavingUtils.save_map(editor.get_editor_world(),'/Game/__FirstRippleQA/Balance'+case)
unreal.log('SWIM_BALANCE_TESTS_BUILT')
