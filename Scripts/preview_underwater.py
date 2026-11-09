import time
from pathlib import Path
import unreal

unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Underwater_1/Maps/Demonstration')
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
starts = [a for a in actors if isinstance(a, unreal.PlayerStart)]
if starts:
    actor = starts[0]
    unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(actor.get_actor_location(), actor.get_actor_rotation())
output = str(Path(unreal.Paths.project_saved_dir()) / 'Screenshots' / 'Underwater_Demonstration_Current.png')
Path(output).parent.mkdir(parents=True, exist_ok=True)
started = time.monotonic()
state = {'requested': False}
def tick(delta):
    elapsed = time.monotonic() - started
    if elapsed > 25 and not state['requested']:
        unreal.AutomationLibrary.take_high_res_screenshot(1280, 720, output)
        state['requested'] = True
    if elapsed > 30 and Path(output).exists():
        unreal.unregister_slate_post_tick_callback(handle)
        unreal.SystemLibrary.quit_editor()
handle = unreal.register_slate_post_tick_callback(tick)

