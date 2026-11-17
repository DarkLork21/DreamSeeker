"""Fix live cursor steering and add non-modal, context-sensitive swimming help."""
import unreal,ast
from pathlib import Path
source=Path(__file__).with_name('build_first_ripple_gameplay.py').read_text();tree=ast.parse(source);nodes=[]
for n in tree.body:
    if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='path' for t in n.targets):break
    nodes.append(n)
exec(compile(ast.Module(body=nodes,type_ignores=[]),'swim_helpers','exec'),globals())
SWIM='/Game/DreamSeeker/Swimming';PAWN=SWIM+'/BP_RhythmSwimmer';CLASS=PAWN+'.BP_RhythmSwimmer_C'
bp=A.load_asset(PAWN);g=unreal.BlueprintGraphEditor.get_graph_editor(L.find_event_graph(bp));G=Graph(g,16000)
assert L.add_member_variable(bp,'HelpOpen',L.get_basic_type_by_name('bool'))
assert L.add_member_variable(bp,'UseMouseSteering',L.get_basic_type_by_name('bool'))
L.set_blueprint_variable_instance_editable(bp,'UseMouseSteering',True)
L.compile_blueprint(bp)
cdo=unreal.get_default_object(bp.generated_class());cdo.set_editor_property('HelpOpen',True);cdo.set_editor_property('UseMouseSteering',True)

controller=G.call('GameplayStatics.GetPlayerController').find_output_pin('ReturnValue')
location=G.call('Actor.K2_GetActorLocation').find_output_pin('ReturnValue')
mouse=G.call('PlayerController.GetMousePosition');G.link(controller,mouse.find_self_pin())
viewport=G.call('PlayerController.GetViewportSize');G.link(controller,viewport.find_self_pin())
project=G.call('PlayerController.ProjectWorldLocationToScreen',WorldLocation=location,bPlayerViewportRelative='true');G.link(controller,project.find_self_pin())
screen=G.call('KismetMathLibrary.BreakVector2D',InVec=project.find_output_pin('ScreenLocation'))
dx=G.math('Subtract_DoubleDouble',A=mouse.find_output_pin('LocationX'),B=screen.find_output_pin('X'))
dz=G.math('Subtract_DoubleDouble',A=screen.find_output_pin('Y'),B=mouse.find_output_pin('LocationY'))
direction=G.call('KismetMathLibrary.MakeVector',X=dx,Y='0',Z=dz).find_output_pin('ReturnValue')
normalized=G.math('Normal',A=direction)
inside_x=G.math('InRange_FloatFloat',Value=mouse.find_output_pin('LocationX'),Min='1',Max=G.math('Subtract_DoubleDouble',A=viewport.find_output_pin('SizeX'),B='1'),InclusiveMin='true',InclusiveMax='true')
inside_y=G.math('InRange_FloatFloat',Value=mouse.find_output_pin('LocationY'),Min='1',Max=G.math('Subtract_DoubleDouble',A=viewport.find_output_pin('SizeY'),B='1'),InclusiveMin='true',InclusiveMax='true')
outside_deadzone=G.math('Greater_DoubleDouble',A=G.math('VSize',A=direction),B='45')
valid=G.math('BooleanAND',A=mouse.find_output_pin('ReturnValue'),B=G.math('BooleanAND',A=project.find_output_pin('ReturnValue'),B=G.math('BooleanAND',A=inside_x,B=G.math('BooleanAND',A=inside_y,B=outside_deadzone))))
valid=G.math('BooleanAND',A=valid,B=G.math('BooleanAND',A=G.read('UseMouseSteering'),B=G.math('Not_PreBool',A=G.read('HelpOpen'))))
target=G.math('SelectVector',A=normalized,B=G.read('AimDirection'),bPickA=valid)
tick=next(n for n in g.list_all_nodes() if str(n.get_node_title()).replace(' ','')=='EventTick')
aim_set=next(n for n in g.list_all_nodes() if str(n.get_node_title()).replace(' ','')=='SetAimDirection')
aim_set.find_input_pin('AimDirection').break_pin_links()
G.put(aim_set.find_input_pin('AimDirection'),G.math('VInterpTo',Current=G.read('AimDirection'),Target=target,DeltaTime=tick.find_output_pin('DeltaSeconds'),InterpSpeed='8'))
# Help never consumes mouse input; it stops propulsion while the player reads.
move=next(n for n in g.list_all_nodes() if str(n.get_node_title()).replace(' ','')=='AddMovementInput' and n.find_input_pin('ScaleValue').list_connected_pins())
old=move.find_input_pin('ScaleValue').list_connected_pins()[0];move.find_input_pin('ScaleValue').break_pin_links()
G.put(move.find_input_pin('ScaleValue'),G.math('SelectFloat',A='0',B=old,bPickA=G.read('HelpOpen')))
current_move=next(n for n in g.list_all_nodes() if str(n.get_node_title()).replace(' ','')=='AddMovementInput' and not n.find_input_pin('ScaleValue').list_connected_pins())
G.put(current_move.find_input_pin('ScaleValue'),G.math('SelectFloat',A='0',B='.20',bPickA=G.read('HelpOpen')))
for raw in L.list_graphs(bp):
    if raw.get_name() not in ('KickLeft','KickRight'):continue
    fg=unreal.BlueprintGraphEditor.get_graph_editor(raw);F=Graph(fg,3000)
    first=fg.find_graph_entry_pin().list_connected_pins()[0];fg.find_graph_entry_pin().break_pin_links()
    allow=F.branch(fg.find_graph_entry_pin(),F.math('Not_PreBool',A=F.read('HelpOpen')))
    F.link(allow.find_then_pin(),first)

key=G.key('H',15500)
e=G.set(key.find_output_pin('Pressed'),'HelpOpen',G.math('Not_PreBool',A=G.read('HelpOpen')))
e=G.set(e,'StrokePower','0');e=G.set(e,'Sprinting','false')
motion=G.read('CharacterMovement');stop=G.do(e,'MovementComponent.StopMovementImmediately');G.link(motion,stop.find_self_pin())
branch=G.branch(stop.find_then_pin(),G.read('HelpOpen'))
# Place the game cursor ahead of Naia when closing help, giving a clear initial direction.
e=G.set(branch.find_else_pin(),'AimDirection','1,0,0')
warp=G.do(e,'PlayerController.SetMouseLocation',X=G.math('Add_DoubleDouble',A=screen.find_output_pin('X'),B='260'),Y=G.math('Add_DoubleDouble',A=screen.find_output_pin('Y'),B='35'));G.link(controller,warp.find_self_pin())
cursor=G.set(warp.find_then_pin(),'bShowMouseCursor','true','/Script/Engine.PlayerController',controller)
compile_save(bp)

# Native HUD text stays readable on screen and cannot take keyboard focus away from swimming.
factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.HUD)
hud=unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_SwimGuideHUD',SWIM,unreal.Blueprint,factory)
hg=unreal.BlueprintGraphEditor.get_graph_editor(L.find_event_graph(hud));hg.remove_nodes(hg.list_all_nodes());H=Graph(hg,0)
draw=L.add_event_override(hud,'ReceiveDrawHUD',unreal.IntPoint(0,-300))
player=H.call('GameplayStatics.GetPlayerPawn').find_output_pin('ReturnValue')
cast=hg.create_node_from_name('Utilities|Casting|CastToActor',unreal.Vector2D(250,-300),[])
assert hg.retarget_node_class(cast,unreal.Actor.static_class(),bp.generated_class())
H.link(draw.find_then_pin(),cast.find_execute_pin());H.link(player,cast.find_input_pin('Object'))
pawn=next(p for p in cast.list_output_pins() if str(p.get_pin_name()).startswith('As'))
loc=H.call('Actor.K2_GetActorLocation');H.link(pawn,loc.find_self_pin());xyz=H.call('KismetMathLibrary.BreakVector',InVec=loc.find_output_pin('ReturnValue'))
x=xyz.find_output_pin('X')
texts=[
('HOME SHALLOWS','Point into the water ahead of Naia.\nTap A, then D, then A: each tap is one kick.\nA/D do NOT mean left/right travel. The mouse steers.\nHolding a kick key does not keep swimming.'),
('FIND YOUR RHYTHM','Alternate A and D at a steady pace: about two kicks/second.\nAfter four good alternating kicks, rhythm restores lucidity.\nMissed beats stop recovery without directly draining the bar.\nRepeated same-side taps do not build speed.'),
('YOUR FIRST DIVE','Aim the mouse BELOW Naia, then alternate A and D.\nSwim beneath the fallen willow; follow the underwater lights.\nAim above Naia to rise on the other side.\nThis lesson has no oxygen timer.'),
('CROSS THE CURRENT','Keep alternating A and D while aiming toward the lantern.\nHold LEFT SHIFT while kicking to sprint through the current.\nSprinting spends lucidity and never restores it.\nRelease Shift and find your rhythm to recover.'),
('THE LANTERN LANDING','Rise toward the surface and reach the final lantern.\nFinish the crossing after making the dive to restore a memory.\nB returns to the hub without completing the dream.\nEscape opens the pause menu.')]
title=texts[0][0];body=texts[0][1]
for threshold,(heading,detail) in zip((2100,4200,7200,9200),texts[1:]):
    cond=H.math('GreaterEqual_DoubleDouble',A=x,B=str(threshold))
    title=H.math('SelectString',A=heading,B=title,bPickA=cond);body=H.math('SelectString',A=detail,B=body,bPickA=cond)
hint=H.call('KismetStringLibrary.Concat_StrStr',A='[H] SWIMMING HELP  -  ',B=title).find_output_pin('ReturnValue')
scale=H.math('FClamp',Value=H.math('Divide_DoubleDouble',A=draw.find_output_pin('SizeX'),B='1200'),Min='.8',Max='1.25')
e=H.do(cast.find_then_pin(),'HUD.DrawText',Text=hint,TextColor='(R=1,G=0.95,B=0.72,A=1)',ScreenX='40',ScreenY='112',Scale=scale).find_then_pin()
# Draw the steering direction beside Naia when help is closed.
open_help=H.read('HelpOpen',CLASS,pawn);toggle=H.branch(e,open_help)
panel=H.do(toggle.find_then_pin(),'HUD.DrawRect',RectColor='(R=0.015,G=0.035,B=0.05,A=.94)',ScreenX='30',ScreenY='155',ScreenW=H.math('Min',A='1050',B=H.math('Subtract_DoubleDouble',A=draw.find_output_pin('SizeX'),B='60')),ScreenH='230')
e=H.do(panel.find_then_pin(),'HUD.DrawText',Text=title,TextColor='(R=1,G=.85,B=.5,A=1)',ScreenX='50',ScreenY='175',Scale=scale).find_then_pin()
e=H.do(e,'HUD.DrawText',Text=body,TextColor='(R=.94,G=.97,B=1,A=1)',ScreenX='50',ScreenY='215',Scale=scale).find_then_pin()
H.do(e,'HUD.DrawText',Text='[H] CLOSE HELP AND SWIM   -   movement rests while help is open',TextColor='(R=1,G=.85,B=.5,A=1)',ScreenX='50',ScreenY='350',Scale=scale)
project=H.call('HUD.Project',Location=loc.find_output_pin('ReturnValue'))
pos=H.call('KismetMathLibrary.BreakVector',InVec=project.find_output_pin('ReturnValue'))
aim=H.read('AimDirection',CLASS,pawn)
tip=H.math('Add_VectorVector',A=loc.find_output_pin('ReturnValue'),B=H.math('Multiply_VectorFloat',A=aim,B='200'))
endpoint=H.call('HUD.Project',Location=tip)
end=H.call('KismetMathLibrary.BreakVector',InVec=endpoint.find_output_pin('ReturnValue'))
line=H.do(toggle.find_else_pin(),'HUD.DrawLine',StartScreenX=pos.find_output_pin('X'),StartScreenY=pos.find_output_pin('Y'),EndScreenX=end.find_output_pin('X'),EndScreenY=end.find_output_pin('Y'),LineColor='(R=.95,G=.82,B=.35,A=.95)',LineThickness='3')
H.do(line.find_then_pin(),'HUD.DrawRect',RectColor='(R=1,G=.9,B=.45,A=1)',ScreenX=H.math('Subtract_DoubleDouble',A=end.find_output_pin('X'),B='3'),ScreenY=H.math('Subtract_DoubleDouble',A=end.find_output_pin('Y'),B='3'),ScreenW='6',ScreenH='6')
compile_save(hud)
mode=A.load_asset('/Game/DreamSeeker/Levels/FirstRipple/BP_FirstRippleMode');unreal.get_default_object(mode.generated_class()).set_editor_property('hud_class',hud.generated_class());assert A.save_loaded_asset(mode,False)
unreal.log('SWIM_STEERING_HELP_FIXED')
