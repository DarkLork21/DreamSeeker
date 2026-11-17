# Against the Tide — Level 2 playable race

Enter the second cloud in the Memory Causeway. A four-second countdown starts a single-length competition against three swimmers in separate background lanes.

Mouse aims, alternating A/D taps propel the swimmer, and Left Shift sprints. Each well-timed alternating kick restores 5 lucidity when not sprinting; sprinting spends 9 per active second. The existing team lucidity component and widget are reused. The protagonist remains unnamed in displayed text.

The coral rival starts fast and slows after ten seconds. The ivory rival maintains a steady pace. The violet rival accelerates after sixteen seconds. Speeds follow fixed race-time rules rather than following the player's position. The HUD shows position and four colored progress tracks.

Finish first to complete the dream. A victory freezes the race, displays confirmation, saves DreamSeeker.Memory.02, and returns to the hub after three seconds. Losing shows a retry message and reloads the race without awarding a seal. Empty lucidity triggers the shared failure screen and restarts the current dream with a full bar. B returns to the hub without completion; Escape uses the existing pause menu.

Completed hub clouds display a gold beacon and DREAM COMPLETE label, loaded from each dream's saved seal. Level 1 uses DreamSeeker.Memory.01. These persist between sessions; replaying or losing does not remove previously earned seals.

Original /Game/Level_2_Swimming is preserved. The new map is /Game/DreamSeeker/Levels/AgainstTheTide/LV_AgainstTheTide. The current scene uses native materials, pool architecture, instanced tiles and lane ropes, spectators, and simple swimming character proxies. Concept illustrations are not imported as game assets. Final character models, production animation, sound and broader player testing remain future work.

## Verification

Runtime checks cover a winning sprint/recovery playthrough, normal-swimming loss and automatic retry, empty-lucidity restart, second-cloud travel, correct completion slots, and missing asset or Blueprint errors. Test saves use DreamSeeker.QA.Race.* slots; test maps are in /Game/__RaceQA and are excluded from the Windows package.

## Authoring scripts

These scripts author assets through Unreal's Python editor interface. Run them deliberately in order when rebuilding this level: build_race_gameplay.py, build_race_scene.py, test_race.py, refine_race.py, finish_race_feedback.py. Scene creation rebuilds the new race map; it does not replace the team's original swimming map. validate_race.py checks the saved assets and recorded runtime logs. The scripts use the existing FirstRipple graph helpers.
