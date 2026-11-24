"""Author reusable swimming Blueprints using the team's existing lucidity component."""
import unreal

A=unreal.EditorAssetLibrary; L=unreal.BlueprintEditorLibrary
ROOT='/Game/DreamSeeker/Swimming'; HUB='/Game/DreamSeeker/DreamHub/MemoryCauseway'
sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
data=unreal.SubobjectDataBlueprintFunctionLibrary

def check(v,label):
    if not v: raise RuntimeError(label)
    return v

def compile_save(bp):
    L.compile_blueprint(bp)
    for raw in L.list_graphs(bp):
        g=unreal.BlueprintGraphEditor.get_graph_editor(raw)
        check(not g.list_nodes_with_errors(),bp.get_name()+' '+raw.get_name())
    check(A.save_loaded_asset(bp,False),'save '+bp.get_name())

class Graph:
    def __init__(self,g,y=5000): self.g=g;self.i=0;self.y=y
    def pos(self,n):
        check(n,'node');n.set_node_pos(unreal.IntPoint((self.i%8)*290,self.y+(self.i//8)*220));self.i+=1;return n
    def call(self,name,**values):
        n=self.pos(self.g.add_call_function_node(name if name.startswith('/') else '/Script/Engine.'+name))
        for k,v in values.items():self.put(n.find_input_pin(k),v)
        return n
    def put(self,p,v):
        if hasattr(v,'try_create_connection'): check(v.try_create_connection(p),'connect '+str(v.get_pin_name())+' -> '+str(p.get_pin_name()))
        else: check(p.set_pin_value(str(v)),'value '+str(p.get_pin_name())+' '+str(v))
    def link(self,a,b):self.put(b,a)
    def read(self,name,owner=None,target=None):
        n=self.pos(self.g.add_get_member_variable_node(name,owner) if owner else self.g.add_get_member_variable_node(name))
        if target:self.link(target,n.find_self_pin())
        return n.find_output_pin(name)
    def set(self,exec,name,value,owner=None,target=None):
        n=self.pos(self.g.add_set_member_variable_node(name,owner) if owner else self.g.add_set_member_variable_node(name))
        self.put(n.find_input_pin(name),value)
        if target:self.link(target,n.find_self_pin())
        self.link(exec,n.find_execute_pin());return n.find_then_pin()
    def math(self,name,**values):return self.call('KismetMathLibrary.'+name,**values).find_output_pin('ReturnValue')
    def branch(self,exec,condition):
        n=self.pos(self.g.add_branch_node());self.link(exec,n.find_execute_pin());self.put(n.find_input_pin('Condition'),condition);return n
    def do(self,exec,name,**values):
        n=self.call(name,**values);self.link(exec,n.find_execute_pin());return n
    def key(self,key,y):return self.g.create_node_from_name('Input|KeyboardEvents|'+key,unreal.Vector2D(0,y),[])

path=ROOT+'/BP_RhythmSwimmer'
if A.does_asset_exist(path):
    # A failed first build may be safely resumed; the saved hub source is untouched.
    bp=A.load_asset(path)
else:bp=check(A.duplicate_asset(HUB+'/BP_MemoryWisp',path),'duplicate swimmer')
g=unreal.BlueprintGraphEditor.get_graph_editor(L.find_event_graph(bp))
# Keep the already-tested pause menu and input-focus chain, replace only movement.
remove=[n for n in g.list_all_nodes() if n.get_node_pos().y<2900 and 'BeginPlay' not in str(n.get_node_title()).replace(' ','')]
g.remove_nodes(remove)
names={'StrokePower':('float','0'),'LastKickTime':('float','-10'),'LastKickLeft':('bool','false'),'GoodStreak':('float','0'),
       'Sprinting':('bool','false'),'AllowRhythmRecovery':('bool','true'),'AimDirection':('vector','1,0,0'),
       'CompletedCrossing':('bool','false'),'VisitedDive':('bool','false'),'CheckpointX':('float','240')}
vector_node=g.add_call_function_node('/Script/Engine.KismetMathLibrary.MakeVector')
vector_type=vector_node.find_output_pin('ReturnValue').get_pin_type()
for name,(kind,default) in names.items():
    if L.add_member_variable(bp,name,vector_type if kind=='vector' else L.get_basic_type_by_name('real' if kind=='float' else kind)):
        pass
g.remove_nodes([vector_node])
L.compile_blueprint(bp)
cdo=unreal.get_default_object(bp.generated_class())
for name,(_,default) in names.items():
    val=unreal.Vector(1,0,0) if name=='AimDirection' else (default=='true' if names[name][0]=='bool' else float(default))
    cdo.set_editor_property(name,val)
L.set_blueprint_variable_instance_editable(bp,'AllowRhythmRecovery',True)
handles=sub.k2_gather_subobject_data_for_blueprint(bp)
root=handles[0];has_lucidity=False
for h in handles:
    obj=data.get_object_for_blueprint(data.get_data(h),bp)
    if isinstance(obj,unreal.StaticMeshComponent):obj.set_editor_property('visible',False)
    if isinstance(obj,unreal.CameraComponent):
        obj.set_editor_property('relative_location',unreal.Vector(280,2400,370));obj.set_editor_property('ortho_width',2450)
        obj.set_editor_property('relative_rotation',unreal.Rotator(0,-5,-90))
    if obj and obj.get_class().get_name()=='BPC_Lucidity_C':has_lucidity=True
if not has_lucidity:
    handle,error=sub.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root,new_class=A.load_blueprint_class('/Game/DreamSeeker/Blueprints/Components/BPC_Lucidity'),blueprint_context=bp))
    check(not str(error),str(error));sub.rename_subobject(handle,unreal.Text('Lucidity'))
L.compile_blueprint(bp)
G=Graph(g)
motion=G.read('CharacterMovement')
controller=G.call('GameplayStatics.GetPlayerController').find_output_pin('ReturnValue')
lucidity=G.read('Lucidity')
lucidity_path='/Game/DreamSeeker/Blueprints/Components/BPC_Lucidity.BPC_Lucidity_C'
widget_path='/Game/DreamSeeker/UI/WBP_LucidityBar.WBP_LucidityBar_C'
# Append initialisation to the existing input-focus BeginPlay chain.
cursor=next(n for n in g.list_all_nodes() if n.get_node_pos().x==600 and n.get_node_pos().y==4200)
cursor.find_then_pin().break_pin_links()
e=G.set(cursor.find_then_pin(),'bShowMouseCursor','true','/Script/Engine.PlayerController',controller)
mode=G.do(e,'CharacterMovementComponent.SetMovementMode',NewMovementMode='MOVE_Flying');G.link(motion,mode.find_self_pin());e=mode.find_then_pin()
create=G.do(e,'/Script/UMG.WidgetBlueprintLibrary.Create',WidgetType=widget_path,OwningPlayer=controller)
cast_name='Utilities|Casting|CastToCharacter'
cast=G.pos(g.create_node_from_name(cast_name,unreal.Vector2D(0,6000),[]))
check(g.retarget_node_class(cast,unreal.Character.static_class(),A.load_blueprint_class('/Game/DreamSeeker/UI/WBP_LucidityBar')),'retarget widget cast')
G.link(create.find_then_pin(),cast.find_execute_pin());G.link(create.find_output_pin('ReturnValue'),cast.find_input_pin('Object'))
typed=next(p for p in cast.list_output_pins() if str(p.get_pin_name()).startswith('As'))
e=G.set(cast.find_then_pin(),'LucidityComponent',lucidity,widget_path,typed)
show=G.do(e,'/Script/UMG.UserWidget.AddToViewport');G.link(create.find_output_pin('ReturnValue'),show.find_self_pin())

def lucidity_call(builder,exec,name,amount):
    n=builder.do(exec,lucidity_path+':'+name,Amount=amount);builder.link(builder.read('Lucidity'),n.find_self_pin());return n.find_then_pin()

# Exposed functions let all swimming dreams reuse exactly the same kick logic.
for key,is_left in (('A',True),('D',False)):
    name='KickLeft' if is_left else 'KickRight'
    old=next((raw for raw in L.list_graphs(bp) if raw.get_name()==name),None)
    if old: L.remove_function_graph(bp,old)
    fg=unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp,name);fg.set_function_is_public();F=Graph(fg,0)
    now=F.call('GameplayStatics.GetTimeSeconds').find_output_pin('ReturnValue')
    gap=F.math('Subtract_DoubleDouble',A=now,B=F.read('LastKickTime'))
    alternate=F.math('NotEqual_BoolBool',A=F.read('LastKickLeft'),B=str(is_left).lower())
    valid=F.math('BooleanAND',A=alternate,B=F.math('Greater_DoubleDouble',A=gap,B='.16'))
    perfect=F.math('BooleanAND',A=valid,B=F.math('InRange_FloatFloat',Value=gap,Min='.30',Max='.75',InclusiveMin='true',InclusiveMax='true'))
    gain=F.math('SelectFloat',A='.60',B='.08',bPickA=valid)
    power=F.math('FClamp',Value=F.math('Add_DoubleDouble',A=F.read('StrokePower'),B=gain),Min='0',Max='1')
    e=F.set(fg.find_graph_entry_pin(),'StrokePower',power)
    streak=F.math('SelectFloat',A=F.math('Add_DoubleDouble',A=F.read('GoodStreak'),B='1'),B='0',bPickA=perfect)
    e=F.set(e,'GoodStreak',streak);e=F.set(e,'LastKickTime',now);e=F.set(e,'LastKickLeft',str(is_left).lower())
    ready=F.math('BooleanAND',A=F.math('GreaterEqual_DoubleDouble',A=F.read('GoodStreak'),B='4'),B=F.math('BooleanAND',A=F.read('AllowRhythmRecovery'),B=F.math('Not_PreBool',A=F.read('Sprinting'))))
    branch=F.branch(e,ready);lucidity_call(F,branch.find_then_pin(),'RestoreLucidity','1.5')
    L.compile_blueprint(bp)
    event=G.key(key,7000 if is_left else 7300)
    fn=G.do(event.find_output_pin('Pressed'),path+'.BP_RhythmSwimmer_C:'+name)

shift=G.key('LeftShift',7600)
G.set(shift.find_output_pin('Pressed'),'Sprinting','true');G.set(shift.find_output_pin('Released'),'Sprinting','false')
# Pausing never leaves the sprint button latched after a focus change.
pause_create=next(n for n in g.list_all_nodes() if n.get_node_pos().x==550 and n.get_node_pos().y==3420)
previous=pause_create.find_execute_pin().list_connected_pins()[0];pause_create.find_execute_pin().break_pin_links()
G.link(G.set(previous,'Sprinting','false'),pause_create.find_execute_pin())

tick=L.add_event_override(bp,'ReceiveTick',unreal.IntPoint(0,8000));T=Graph(g,8200)
dt=tick.find_output_pin('DeltaSeconds')
deproject=T.call('PlayerController.DeprojectMousePositionToWorld');T.link(controller,deproject.find_self_pin())
end=T.math('Add_VectorVector',A=deproject.find_output_pin('WorldLocation'),B=T.math('Multiply_VectorFloat',A=deproject.find_output_pin('WorldDirection'),B='100000'))
hit=T.call('KismetMathLibrary.LinePlaneIntersection_OriginNormal',LineStart=deproject.find_output_pin('WorldLocation'),LineEnd=end,PlaneOrigin='0,0,0',PlaneNormal='0,1,0')
location=T.call('Actor.K2_GetActorLocation').find_output_pin('ReturnValue')
aim=T.math('GetDirectionUnitVector',From=location,To=hit.find_output_pin('Intersection'))
aim=T.math('SelectVector',A=aim,B=T.read('AimDirection'),bPickA=deproject.find_output_pin('ReturnValue'))
smooth=T.math('VInterpTo',Current=T.read('AimDirection'),Target=aim,DeltaTime=dt,InterpSpeed='4')
e=T.set(tick.find_then_pin(),'AimDirection',smooth)
power=T.math('FClamp',Value=T.math('Subtract_DoubleDouble',A=T.read('StrokePower'),B=T.math('Multiply_DoubleDouble',A=dt,B='.75')),Min='0',Max='1')
e=T.set(e,'StrokePower',power)
current=T.read('CurrentLucidity',lucidity_path,lucidity)
can_sprint=T.math('BooleanAND',A=T.read('Sprinting'),B=T.math('Greater_DoubleDouble',A=current,B='0'))
speed=T.math('SelectFloat',A='580',B='330',bPickA=can_sprint)
e=T.set(e,'MaxFlySpeed',speed,'/Script/Engine.CharacterMovementComponent',motion)
move=T.do(e,'Pawn.AddMovementInput',WorldDirection=T.read('AimDirection'),ScaleValue=T.read('StrokePower'));e=move.find_then_pin()
cost=T.math('SelectFloat',A=T.math('Multiply_DoubleDouble',A=dt,B='9'),B='0',bPickA=T.math('BooleanAND',A=can_sprint,B=T.math('Greater_DoubleDouble',A=T.read('StrokePower'),B='.1')))
e=lucidity_call(T,e,'ConsumeLucidity',cost)
xyz=T.call('KismetMathLibrary.BreakVector',InVec=location)
# Keep the swimming corridor bounded and just below the surface; no drowning trap.
clamp=T.call('KismetMathLibrary.MakeVector',X=T.math('FClamp',Value=xyz.find_output_pin('X'),Min='200',Max='10850'),Y='0',Z=T.math('FClamp',Value=xyz.find_output_pin('Z'),Min='-440',Max='-25'))
bounded=T.do(e,'Actor.K2_SetActorLocation',NewLocation=clamp.find_output_pin('ReturnValue'),bSweep='true');e=bounded.find_then_pin()
in_dive=T.math('BooleanAND',A=T.math('InRange_FloatFloat',Value=xyz.find_output_pin('X'),Min='4700',Max='6300',InclusiveMin='true',InclusiveMax='true'),B=T.math('Less_DoubleDouble',A=xyz.find_output_pin('Z'),B='-170'))
e=T.set(e,'VisitedDive',T.math('BooleanOR',A=T.read('VisitedDive'),B=in_dive))
end_condition=T.math('BooleanAND',A=T.math('Greater_DoubleDouble',A=xyz.find_output_pin('X'),B='10400'),B=T.math('BooleanAND',A=T.read('VisitedDive'),B=T.math('Not_PreBool',A=T.read('CompletedCrossing'))))
win=T.branch(e,end_condition);e=T.set(win.find_then_pin(),'CompletedCrossing','true')
find=T.do(e,'GameplayStatics.GetActorOfClass',ActorClass=HUB+'/BP_DreamCompletion.BP_DreamCompletion_C')
cast=T.pos(g.create_node_from_name('Utilities|Casting|CastToActor',unreal.Vector2D(0,12000),[]))
check(g.retarget_node_class(cast,unreal.Actor.static_class(),A.load_blueprint_class(HUB+'/BP_DreamCompletion')),'completion cast')
T.link(find.find_then_pin(),cast.find_execute_pin());T.link(find.find_output_pin('ReturnValue'),cast.find_input_pin('Object'))
complete=T.do(cast.find_then_pin(),HUB+'/BP_DreamCompletion.BP_DreamCompletion_C:CompleteDream');T.link(next(p for p in cast.list_output_pins() if str(p.get_pin_name()).startswith('As')),complete.find_self_pin())
# A gentle current in section four, independent of sprint or rhythm.
in_current=T.math('InRange_FloatFloat',Value=xyz.find_output_pin('X'),Min='7400',Max='8600',InclusiveMin='true',InclusiveMax='true')
flow=T.branch(win.find_else_pin(),in_current)
current_move=T.do(flow.find_then_pin(),'Pawn.AddMovementInput',WorldDirection='-1,0,0',ScaleValue='.20')
L.compile_blueprint(bp)
cdo=unreal.get_default_object(bp.generated_class());motion=cdo.get_component_by_class(unreal.CharacterMovementComponent)
for name,value in {'gravity_scale':0.0,'max_fly_speed':330.0,'braking_deceleration_flying':210.0,'max_acceleration':950.0}.items():motion.set_editor_property(name,value)
cdo.get_component_by_class(unreal.CapsuleComponent).set_capsule_size(22,38)
compile_save(bp)
unreal.log('SWIM_GAMEPLAY_BUILT')
