"""Race rules and opponents built on the established swimming controls."""
import unreal,ast
from pathlib import Path
helper=Path(__file__).parent.parent/'FirstRipple/build_first_ripple_gameplay.py'
source=helper.read_text();tree=ast.parse(source);nodes=[]
for n in tree.body:
    if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='path' for t in n.targets):break
    nodes.append(n)
exec(compile(ast.Module(body=nodes,type_ignores=[]),'helpers','exec'),globals())
ROOT='/Game/DreamSeeker/Levels/AgainstTheTide';HUB='/Game/DreamSeeker/DreamHub/MemoryCauseway';SWIM='/Game/DreamSeeker/Swimming'
tools=unreal.AssetToolsHelpers.get_asset_tools()
def blueprint(name,parent=unreal.Actor):
    if A.does_asset_exist(ROOT+'/'+name):return A.load_asset(ROOT+'/'+name)
    f=unreal.BlueprintFactory();f.set_editor_property('parent_class',parent);return tools.create_asset(name,ROOT,unreal.Blueprint,f)
def variable(bp,name,kind,default=None,editable=False):
    L.add_member_variable(bp,name,L.get_basic_type_by_name(kind));L.compile_blueprint(bp)
    if default is not None:unreal.get_default_object(bp.generated_class()).set_editor_property(name,default)
    if editable:L.set_blueprint_variable_instance_editable(bp,name,True)
def component(bp,kind,name):
    for h in sub.k2_gather_subobject_data_for_blueprint(bp):
        o=data.get_object_for_blueprint(data.get_data(h),bp)
        if o and o.get_name()==name:return o
    h,err=sub.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=sub.k2_gather_subobject_data_for_blueprint(bp)[0],new_class=kind,blueprint_context=bp));assert not str(err),err
    sub.rename_subobject(h,unreal.Text(name));return data.get_object_for_blueprint(data.get_data(h),bp)
def cast(G,e,obj,bp):
    n=G.pos(G.g.create_node_from_name('Utilities|Casting|CastToActor',unreal.Vector2D(),[]));assert G.g.retarget_node_class(n,unreal.Actor.static_class(),bp.generated_class());G.link(e,n.find_execute_pin());G.link(obj,n.find_input_pin('Object'));return n,next(p for p in n.list_output_pins() if str(p.get_pin_name()).startswith('As'))
def bypass(g,n):
    ins=n.find_execute_pin().list_connected_pins();outs=n.find_then_pin().list_connected_pins()
    n.find_execute_pin().break_pin_links();n.find_then_pin().break_pin_links()
    for i in ins:
        for o in outs:assert i.try_create_connection(o)
    g.remove_nodes([n])
racepath=ROOT+'/BP_RaceSwimmer';pawn=A.load_asset(racepath) if A.does_asset_exist(racepath) else A.duplicate_asset(SWIM+'/BP_RhythmSwimmer',racepath)
variable(pawn,'RaceLocked','bool',True)
g=unreal.BlueprintGraphEditor.get_graph_editor(L.find_event_graph(pawn));G=Graph(g,38000)
for n in list(g.list_all_nodes()):
    title=str(n.get_node_title()).replace(' ','')
    if title in ('AddActorWorldOffset','UpdateTimedLesson'):bypass(g,n)
tick=next(n for n in g.list_all_nodes() if str(n.get_node_title()).replace(' ','')=='EventTick')
if not any('RaceLocked' in str(n.get_node_title()) for n in g.list_all_nodes()):
    old=tick.find_then_pin().list_connected_pins()[0];tick.find_then_pin().break_pin_links();b=G.branch(tick.find_then_pin(),G.math('Not_PreBool',A=G.read('RaceLocked')));G.link(b.find_then_pin(),old)
compile_save(pawn)
# Opponents occupy separate visual lanes and never collide with the player.
rival=blueprint('BP_RaceRival');variable(rival,'BaseSpeed','real',350.0,True);variable(rival,'RaceStyle','int',0,True)
variable(rival,'LaneY','real',-300.0,True);variable(rival,'Progress','real',350.0)
for name,mesh,xyz,scale,material in (
 ('Body','Sphere',(0,0,0),(1.2,.32,.25),'M_NaiaDress'),('Head','Sphere',(65,0,10),(.30,.30,.30),'M_NaiaSkin'),
 ('LeftArm','Cube',(65,22,-7),(.85,.12,.12),'M_NaiaSkin'),('RightArm','Cube',(10,-22,-7),(.85,.12,.12),'M_NaiaSkin'),
 ('LeftLeg','Cube',(-91,14,-4),(.85,.12,.15),'M_NaiaSkin'),('RightLeg','Cube',(-91,-14,-4),(.85,.12,.15),'M_NaiaSkin'),
 ('RaceCap','Sphere',(64,0,24),(.32,.32,.18),'M_NaiaDress')):
    c=component(rival,unreal.StaticMeshComponent,name);c.set_static_mesh(A.load_asset('/Engine/BasicShapes/'+mesh));c.set_material(0,A.load_asset('/Game/DreamSeeker/Levels/FirstRipple/Materials/'+material));c.set_collision_profile_name('NoCollision');c.set_editor_property('relative_location',unreal.Vector(*xyz));c.set_editor_property('relative_scale3d',unreal.Vector(*scale))
compile_save(rival)
manager=blueprint('BP_RaceDirector');MC=ROOT+'/BP_RaceDirector.BP_RaceDirector_C';PC=racepath+'.BP_RaceSwimmer_C';RC=ROOT+'/BP_RaceRival.BP_RaceRival_C'
for name,kind,default in (('RaceTime','real',0.0),('Countdown','real',4.0),('Started','bool',False),('Finished','bool',False),('PlayerWon','bool',False),('Rival1X','real',350.0),('Rival2X','real',350.0),('Rival3X','real',350.0),('RacePosition','int',1),('FinishX','real',8000.0)):
    variable(manager,name,kind,default, name=='FinishX')
for name,bp in (('Player',pawn),('Rival1',rival),('Rival2',rival),('Rival3',rival)):
    L.add_member_variable(manager,name,L.get_object_reference_type(bp.generated_class()));L.set_blueprint_variable_instance_editable(manager,name,name!='Player')
L.compile_blueprint(manager)
g=unreal.BlueprintGraphEditor.get_graph_editor(L.find_event_graph(manager));g.remove_nodes(g.list_all_nodes())
events={name:g.add_custom_event_node(name) for name in ('WinRace','LoseRace')};L.compile_blueprint(manager);G=Graph(g,0)
begin=L.add_event_override(manager,'ReceiveBeginPlay',unreal.IntPoint(0,0));p=G.call('GameplayStatics.GetPlayerPawn').find_output_pin('ReturnValue');c,p=cast(G,begin.find_then_pin(),p,pawn);G.set(c.find_then_pin(),'Player',p)
tick=L.add_event_override(manager,'ReceiveTick',unreal.IntPoint(0,1000));T=Graph(g,1300);dt=tick.find_output_pin('DeltaSeconds');p=T.read('Player');health=T.read('CurrentLucidity','/Game/DreamSeeker/Blueprints/Components/BPC_Lucidity.BPC_Lucidity_C',T.read('Lucidity',PC,p))
active=T.branch(tick.find_then_pin(),T.math('BooleanAND',A=T.math('Not_PreBool',A=T.read('Finished')),B=T.math('Not_PreBool',A=T.read('DreamFailed',PC,p))))
started=T.branch(active.find_then_pin(),T.read('Started'))
e=T.set(started.find_else_pin(),'Countdown',T.math('Subtract_DoubleDouble',A=T.read('Countdown'),B=dt))
go=T.branch(e,T.math('LessEqual_DoubleDouble',A=T.read('Countdown'),B='0'));e=T.set(go.find_then_pin(),'Started','true');T.set(e,'RaceLocked','false',PC,p)
e=T.set(started.find_then_pin(),'RaceTime',T.math('Add_DoubleDouble',A=T.read('RaceTime'),B=dt))
for i,base in ((1,430),(2,355),(3,320)):
    speed=T.math('SelectFloat',A='315',B='430',bPickA=T.math('Greater_DoubleDouble',A=T.read('RaceTime'),B='10')) if i==1 else (T.math('SelectFloat',A='430',B='320',bPickA=T.math('Greater_DoubleDouble',A=T.read('RaceTime'),B='16')) if i==3 else '355')
    e=T.set(e,f'Rival{i}X',T.math('Add_DoubleDouble',A=T.read(f'Rival{i}X'),B=T.math('Multiply_DoubleDouble',A=dt,B=speed)))
    rivalref=T.read(f'Rival{i}');x=T.read(f'Rival{i}X');bob=T.math('Multiply_DoubleDouble',A=T.math('Sin',A=T.math('Multiply_DoubleDouble',A=T.read('RaceTime'),B=str(5+i))),B='5')
    loc=T.call('KismetMathLibrary.MakeVector',X=x,Y=str(-300*i),Z=T.math('Add_DoubleDouble',A=bob,B='-38')).find_output_pin('ReturnValue')
    n=T.do(e,'Actor.K2_SetActorLocation',NewLocation=loc);T.link(rivalref,n.find_self_pin());e=n.find_then_pin()
    # Alternating legs give opponents a readable kick silhouette.
    for part,sign in (('LeftLeg',1),('RightLeg',-1)):
        rot=T.call('KismetMathLibrary.MakeRotator',Pitch=T.math('Multiply_DoubleDouble',A=bob,B=str(sign*3))).find_output_pin('ReturnValue')
        n=T.do(e,'SceneComponent.K2_SetRelativeRotation',NewRotation=rot);T.link(T.read(part,RC,rivalref),n.find_self_pin());e=n.find_then_pin()
loc=T.call('Actor.K2_GetActorLocation');T.link(p,loc.find_self_pin());px=T.call('KismetMathLibrary.BreakVector',InVec=loc.find_output_pin('ReturnValue')).find_output_pin('X')
rank='1'
for i in (1,2,3):rank=T.math('Add_IntInt',A=T.math('SelectInt',A='1',B='0',bPickA=T.math('Greater_DoubleDouble',A=T.read(f'Rival{i}X'),B=px)),B=rank)
e=T.set(e,'RacePosition',rank)
finish=T.branch(e,T.math('GreaterEqual_DoubleDouble',A=px,B=T.read('FinishX')))
win=T.do(finish.find_then_pin(),MC+':WinRace')
first=T.math('FMax',A=T.read('Rival1X'),B=T.math('FMax',A=T.read('Rival2X'),B=T.read('Rival3X')))
lost=T.branch(finish.find_else_pin(),T.math('GreaterEqual_DoubleDouble',A=first,B=T.read('FinishX')));T.do(lost.find_then_pin(),MC+':LoseRace')
# Results freeze input, then either save the second seal or restart the same race.
for won in (True,False):
    event=events['WinRace' if won else 'LoseRace'];F=Graph(g,13000 if won else 17000)
    once=F.branch(event.find_then_pin(),F.math('Not_PreBool',A=F.read('Finished')));e=F.set(once.find_then_pin(),'Finished','true');e=F.set(e,'PlayerWon',str(won).lower());p=F.read('Player');e=F.set(e,'RaceLocked','true',PC,p);e=F.set(e,'StrokePower','0',PC,p)
    n=F.do(e,'MovementComponent.StopMovementImmediately');F.link(F.read('CharacterMovement',PC,p),n.find_self_pin());e=F.do(n.find_then_pin(),'KismetSystemLibrary.Delay',Duration='3').find_then_pin()
    if won:
        n=F.do(e,'GameplayStatics.GetActorOfClass',ActorClass=HUB+'/BP_DreamCompletion.BP_DreamCompletion_C');c,completion=cast(F,n.find_then_pin(),n.find_output_pin('ReturnValue'),A.load_asset(HUB+'/BP_DreamCompletion'));n=F.do(c.find_then_pin(),HUB+'/BP_DreamCompletion.BP_DreamCompletion_C:CompleteDream');F.link(completion,n.find_self_pin())
    else:F.do(e,'GameplayStatics.OpenLevelBySoftObjectPtr',Level=ROOT+'/LV_AgainstTheTide.LV_AgainstTheTide')
compile_save(manager)
# Native HUD: race position, progress, teaching captions, and unambiguous outcomes.
hud=blueprint('BP_RaceHUD',unreal.HUD);g=unreal.BlueprintGraphEditor.get_graph_editor(L.find_event_graph(hud));g.remove_nodes(g.list_all_nodes());H=Graph(g,0)
draw=L.add_event_override(hud,'ReceiveDrawHUD',unreal.IntPoint());n=H.do(draw.find_then_pin(),'GameplayStatics.GetActorOfClass',ActorClass=MC);c,m=cast(H,n.find_then_pin(),n.find_output_pin('ReturnValue'),manager);e=c.find_then_pin()
def text(e,s,x,y,scale='1.5',color='(R=.94,G=.94,B=.91,A=1)'):
    return H.do(e,'HUD.DrawText',Text=s,ScreenX=x,ScreenY=y,Scale=scale,TextColor=color).find_then_pin()
e=text(e,'AGAINST THE TIDE','40','115','1.5','(R=1,G=.75,B=.4,A=1)')
position=H.call('KismetStringLibrary.Conv_IntToString',InInt=H.read('RacePosition',MC,m)).find_output_pin('ReturnValue');label=H.call('KismetStringLibrary.Concat_StrStr',A='POSITION  ',B=position).find_output_pin('ReturnValue');label=H.call('KismetStringLibrary.Concat_StrStr',A=label,B=' / 4').find_output_pin('ReturnValue')
e=text(e,label,'40','148')
p=H.read('Player',MC,m);hp=H.read('CurrentLucidity','/Game/DreamSeeker/Blueprints/Components/BPC_Lucidity.BPC_Lucidity_C',H.read('Lucidity',PC,p))
recent=H.math('Less_DoubleDouble',A=H.math('Subtract_DoubleDouble',A=H.call('GameplayStatics.GetTimeSeconds').find_output_pin('ReturnValue'),B=H.read('LastPerfectTime',PC,p)),B='.45')
hint=H.math('SelectString',A='PERFECT RHYTHM  + LUCIDITY',B='Steady A / D refills lucidity. SHIFT spends it.',bPickA=recent)
hint=H.math('SelectString',A='LOW LUCIDITY - release Shift and find your rhythm.',B=hint,bPickA=H.math('LessEqual_DoubleDouble',A=hp,B='20'))
e=text(e,hint,'40','83','1.2','(R=.65,G=1,B=.78,A=1)')
time=H.read('RaceTime',MC,m);started=H.branch(e,H.read('Started',MC,m));count=H.call('KismetStringLibrary.Conv_IntToString',InInt=H.math('FCeil',A=H.read('Countdown',MC,m))).find_output_pin('ReturnValue')
sx=H.math('Subtract_DoubleDouble',A=H.math('Divide_DoubleDouble',A=draw.find_output_pin('SizeX'),B='2'),B='220')
e=text(started.find_else_pin(),'FIND YOUR RHYTHM',sx,'250','2.5');e=text(e,count,sx,'300','4')
panelY=H.math('Subtract_DoubleDouble',A=draw.find_output_pin('SizeY'),B='130')
lesson=H.math('SelectString',A='Hold SHIFT for short sprints. Release it and alternate A / D to recover.',B='Mouse aims. Tap A / D alternately. Beat all three swimmers to finish first.',bPickA=H.math('Greater_DoubleDouble',A=time,B='7'))
lesson=H.math('SelectString',A='Empty lucidity ends the attempt. Losing the race restarts this level.',B=lesson,bPickA=H.math('Greater_DoubleDouble',A=time,B='16'))
lesson=H.math('SelectString',A='Final stretch - choose your sprint and keep the rhythm!',B=lesson,bPickA=H.math('Greater_DoubleDouble',A=time,B='21'))
e=H.do(started.find_then_pin(),'HUD.DrawRect',RectColor='(R=.025,G=.035,B=.055,A=.85)',ScreenX='30',ScreenY=panelY,ScreenW=H.math('Subtract_DoubleDouble',A=draw.find_output_pin('SizeX'),B='60'),ScreenH='92').find_then_pin()
e=text(e,lesson,'50',H.math('Add_DoubleDouble',A=panelY,B='22'),'1.35')
end=H.branch(e,H.read('Finished',MC,m));e=H.do(end.find_then_pin(),'HUD.DrawRect',RectColor='(R=.015,G=.025,B=.05,A=.88)',ScreenX='0',ScreenY='0',ScreenW=draw.find_output_pin('SizeX'),ScreenH=draw.find_output_pin('SizeY')).find_then_pin()
title=H.math('SelectString',A='FIRST PLACE - DREAM COMPLETE',B='RACE LOST',bPickA=H.read('PlayerWon',MC,m));subtitle=H.math('SelectString',A='Memory restored. Returning to the dream hub...',B='Try again. Restarting this race with full lucidity...',bPickA=H.read('PlayerWon',MC,m))
e=text(e,title,sx,'340','2.4','(R=1,G=.8,B=.45,A=1)');text(e,subtitle,sx,'395','1.5')
failed=H.branch(end.find_else_pin(),H.read('DreamFailed',PC,p));e=H.do(failed.find_then_pin(),'HUD.DrawRect',RectColor='(R=.015,G=.025,B=.05,A=.9)',ScreenX='0',ScreenY='0',ScreenW=draw.find_output_pin('SizeX'),ScreenH=draw.find_output_pin('SizeY')).find_then_pin();e=text(e,'THE DREAM FADES',sx,'340','2.5');text(e,'Lucidity empty. Restarting this race...',sx,'395')
compile_save(hud)
mode=blueprint('BP_RaceMode',unreal.GameModeBase);L.compile_blueprint(mode);cdo=unreal.get_default_object(mode.generated_class());cdo.set_editor_property('default_pawn_class',pawn.generated_class());cdo.set_editor_property('hud_class',hud.generated_class());assert A.save_loaded_asset(mode,False)
unreal.log('RACE_GAMEPLAY_READY')
