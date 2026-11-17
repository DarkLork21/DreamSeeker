# The First Ripple — Level 1 playable candidate

Open Windows/Dream_Seker_Unreal.exe. Choose Start Game, move right through the hub to the first cloud, and press E. The first cloud now opens the home-side swimming lesson. Keep the entire Windows folder together.

## Swimming

- Short automatic lessons appear at the appropriate places and fade away while play continues. There is no H panel or required dismissal. The opening introduces steering and then alternating kicks; later captions teach rhythm, diving, sprinting and finishing.
- Point the mouse in the direction Naia should swim. Turning is smoothed; the camera follows at a fixed angle.
- A gold direction guide shows the current swimming heading. Cursor positions outside the game window and within the small dead zone around Naia leave the previous direction unchanged.
- Tap A and D alternately for left and right kicks. Hold a steady cadence, roughly two kicks per second. Holding a key does not automatically repeat kicks.
- Each perfect alternating kick restores 5 lucidity when not sprinting. The first kick establishes timing; subsequent kicks should be 0.28–0.85 seconds apart. Green feedback confirms recovery.
- Hold Left Shift while kicking to sprint. Sprinting consumes 9 lucidity per second while swimming actively. It cannot restore lucidity at the same time.
- Same-side tapping does not build propulsion or restore lucidity. A missed beat breaks the recovery streak without directly subtracting lucidity.
- Lucidity keeps you in the dream. At 20% or less, an amber warning tells the player to release Shift and recover with perfect rhythm. At zero, movement stops and a failure message appears for 2.5 seconds, then the same dream restarts with full lucidity. This first lesson has no separate oxygen timer.
- Escape opens the existing pause menu. B returns to the hub without awarding completion.

## Route

Home shallows → rhythm pool → dive beneath the fallen willow → sprint-required opposing current → lantern landing. Follow the underwater glimmers beneath the log. Reach the final lantern near the surface after making the dive to complete the dream. Completion saves dream 1's seal and returns to the hub.

## Team integration

All remote team branch tips inspected on 16 November 2026 are ancestors of main e6ab6e0: FishingLevel, Initial-Input, Testart, energy-bar, UI/start_page and main_test_merge. The polished hub and restored fishing-level hub connections were pushed to main. No branch was deleted or history rewritten. The original C:/UnrealProjects checkout and its separate working changes were preserved.

Level 1 is a separate map at /Game/DreamSeeker/Levels/FirstRipple/LV_FirstRipple. The original /Game/Level_1_Learning remains intact. The candidate reuses the team's BPC_Lucidity and WBP_LucidityBar rather than replacing their system. AllowRhythmRecovery on the swimming pawn can be disabled for the final dream; this has been tested.

## Verification and remaining work

The automated runtime check completed the route through the log and current. Perfect rhythm raised a test reserve from 50 to 90; off-rhythm kicks and the disabled final-dream recovery switch left it unchanged. Normal swimming stalled at the current entrance. Sprint crossed in 7.63 seconds with at least 35.8% lucidity remaining. Empty lucidity triggered failure and restarted the same dream at 100%. Runtime checks reported no missing-object access errors. The QA save was removed after testing.

The cursor steering was corrected to use viewport coordinates relative to Naia. Live mouse-and-keyboard movement was confirmed by the player, and recorded movement exceeded X=10,800. The full automated route passed again after the visual and automatic tutorial changes.

## Visual polish pass

The route now uses a continuous sculpted shore, custom willow trunks and drooping foliage, layered distant woodland, a sheltered timber home, quieter materials and lighting, animated water and foliage, underwater depth tint and restrained caustic light. Naia's character proxy turns toward her swimming direction and animates alternating kicks without rotating the camera. Floating instruction labels and the repeated prototype banks were removed.

There are 207 actors and nine detail batches holding 6,242 instances, compared with 844 actors in the preceding candidate. This is an object-count improvement, not a claim about frame rate on other computers. All five sections were rendered and inspected; the final Windows cook and package completed without shader compilation errors. The original learning map remains untouched.

Source assets and Blueprint compilation passed validation. Windows Shipping cooking, staging and packaging completed. Temporary QA maps were excluded from the package.

This is a complete first playable route, with environment geometry and a simple authored character proxy. It is not final production art: Naia's final character, polished swimming animation, sound design, narrative dialogue, accessibility/controller support and broader playtesting remain. Generated concept images were not imported into the game. Other dreams retain the team's existing content; this candidate does not implement their unfinished objectives or the final ending.

The home shallows now begin beyond the pier, with a low sunset, warm lake reflections and violet distant shores. Player-facing lessons keep the protagonist unnamed.
