# The First Ripple — Level 1 playable candidate

Open Windows/Dream_Seker_Unreal.exe. Choose Start Game, move right through the hub to the first cloud, and press E. The first cloud now opens the home-side swimming lesson. Keep the entire Windows folder together.

## Swimming

- Point the mouse in the direction Naia should swim. Turning is smoothed; the camera follows at a fixed angle.
- Tap A and D alternately for left and right kicks. Hold a steady cadence, roughly two kicks per second. Holding a key does not automatically repeat kicks.
- After four well-timed alternating kicks, each good kick restores 1.5 lucidity. The timing window is 0.30–0.75 seconds.
- Hold Left Shift while kicking to sprint. Sprinting consumes 9 lucidity per second while swimming actively. It cannot restore lucidity at the same time.
- Same-side tapping does not build propulsion or restore lucidity. A missed beat breaks the recovery streak without directly subtracting lucidity.
- Zero lucidity still permits normal swimming. This first lesson has no oxygen timer.
- Escape opens the existing pause menu. B returns to the hub without awarding completion.

## Route

Home shallows → rhythm pool → dive beneath the fallen willow → gentle opposing current → lantern landing. Follow the underwater glimmers beneath the log. Reach the final lantern near the surface after making the dive to complete the dream. Completion saves dream 1's seal and returns to the hub.

## Team integration

All remote team branch tips inspected on 16 November 2026 are ancestors of main e6ab6e0: FishingLevel, Initial-Input, Testart, energy-bar, UI/start_page and main_test_merge. The polished hub and restored fishing-level hub connections were pushed to main. No branch was deleted or history rewritten. The original C:/UnrealProjects checkout and its separate working changes were preserved.

Level 1 is a separate map at /Game/DreamSeeker/Levels/FirstRipple/LV_FirstRipple. The original /Game/Level_1_Learning remains intact. The candidate reuses the team's BPC_Lucidity and WBP_LucidityBar rather than replacing their system. AllowRhythmRecovery on the swimming pawn can be disabled for the final dream; this has been tested.

## Verification and remaining work

The automated runtime check traversed the route through the log and current to completion. Same-side taps did not restore lucidity; rhythm raised a test reserve from 50 to 57.5; recovery stayed unchanged with the final-dream switch disabled; sprinting lowered it to 48.35; normal movement continued at zero; visiting the finish before the dive did not complete the dream. The QA save was removed after testing.

Source assets and Blueprint compilation passed validation. Windows Shipping cooking, staging and packaging completed. Temporary QA maps were excluded from the package.

This is a complete first playable route, with environment geometry and a simple authored character proxy. It is not final production art: Naia's final character, polished swimming animation, sound design, narrative dialogue, accessibility/controller support and broader playtesting remain. Generated concept images were not imported into the game. Other dreams retain the team's existing content; this candidate does not implement their unfinished objectives or the final ending.
