import unreal,ast
from pathlib import Path
source=Path(__file__).with_name('build_race_gameplay.py').read_text();exec(source.split('racepath=')[0],globals())
ROOT='/Game/DreamSeeker/Levels/AgainstTheTide';PC=ROOT+'/BP_RaceSwimmer.BP_RaceSwimmer_C';MC=ROOT+'/BP_RaceDirector.BP_RaceDirector_C';LC='/Game/DreamSeeker/Blueprints/Components/BPC_Lucidity.BPC_Lucidity_C'
bp=A.load_asset(ROOT+'/BP_RaceDirector');g=unreal.BlueprintGraphEditor.get_graph_editor(L.find_event_graph(bp));G=Graph(g,27000)
tick=next(n for n in g.list_all_nodes() if str(n.get_node_title()).replace(' ','')=='EventTick');branch=tick.find_then_pin().list_connected_pins()[0].get_owning_node();old=branch.find_input_pin('Condition').list_connected_pins()[0];branch.find_input_pin('Condition').break_pin_links()
health=G.read('CurrentLucidity',LC,G.read('Lucidity',PC,G.read('Player')));G.put(branch.find_input_pin('Condition'),G.math('BooleanAND',A=old,B=G.math('Greater_DoubleDouble',A=health,B='0')));compile_save(bp)
hud=A.load_asset(ROOT+'/BP_RaceHUD');g=unreal.BlueprintGraphEditor.get_graph_editor(L.find_event_graph(hud));H=Graph(g,14000)
c=next(n for n in g.list_all_nodes() if str(n.get_node_title()).startswith('Cast To'));m=next(p for p in c.list_output_pins() if str(p.get_pin_name()).startswith('As'));old=c.find_then_pin().list_connected_pins()[0];c.find_then_pin().break_pin_links()
draw=next(n for n in g.list_all_nodes() if 'DrawHUD' in str(n.get_node_title()).replace(' ',''));size=draw.find_output_pin('SizeX');x=H.math('Subtract_DoubleDouble',A=size,B='325')
e=H.do(c.find_then_pin(),'HUD.DrawRect',RectColor='(R=.02,G=.035,B=.055,A=.78)',ScreenX='28',ScreenY='76',ScreenW='540',ScreenH='102').find_then_pin()
e=H.do(e,'HUD.DrawRect',RectColor='(R=.02,G=.035,B=.055,A=.8)',ScreenX=H.math('Subtract_DoubleDouble',A=x,B='18'),ScreenY='25',ScreenW='300',ScreenH='138').find_then_pin()
e=H.do(e,'HUD.DrawText',Text='RACE PROGRESS',ScreenX=x,ScreenY='35',Scale='1.2',TextColor='(R=1,G=.8,B=.5,A=1)').find_then_pin()
loc=H.call('Actor.K2_GetActorLocation');H.link(H.read('Player',MC,m),loc.find_self_pin());px=H.call('KismetMathLibrary.BreakVector',InVec=loc.find_output_pin('ReturnValue')).find_output_pin('X')
for i,color in enumerate(('(R=.25,G=.85,B=.8,A=1)','(R=1,G=.3,B=.2,A=1)','(R=.9,G=.85,B=.65,A=1)','(R=.65,G=.35,B=.85,A=1)')):
    progress=px if i==0 else H.read('Rival'+str(i)+'X',MC,m)
    progress=H.math('FClamp',Value=H.math('Divide_DoubleDouble',A=H.math('Subtract_DoubleDouble',A=progress,B='350'),B='7650'),Min='0',Max='1')
    y=str(63+i*23)
    e=H.do(e,'HUD.DrawRect',RectColor='(R=.16,G=.18,B=.21,A=1)',ScreenX=x,ScreenY=y,ScreenW='260',ScreenH='10').find_then_pin()
    e=H.do(e,'HUD.DrawRect',RectColor=color,ScreenX=x,ScreenY=y,ScreenW=H.math('Multiply_DoubleDouble',A=progress,B='260'),ScreenH='10').find_then_pin()
H.link(e,old)
# Controls and win condition are visible before the whistle too.
count=next(n for n in g.list_all_nodes() if str(n.get_node_title()).replace(' ','')=='DrawText' and n.find_input_pin('Scale').get_pin_value() in ('4','4.000000'))
e=H.do(count.find_then_pin(),'HUD.DrawText',Text='MOUSE aim   A / D kicks   SHIFT sprint',ScreenX='480',ScreenY='400',Scale='1.5',TextColor='(R=1,G=.92,B=.75,A=1)').find_then_pin()
H.do(e,'HUD.DrawText',Text='Beat every rival. Losing or empty lucidity restarts this race.',ScreenX='430',ScreenY='438',Scale='1.3',TextColor='(R=1,G=.92,B=.75,A=1)')
compile_save(hud)
unreal.log('RACE_FEEDBACK_READY')
