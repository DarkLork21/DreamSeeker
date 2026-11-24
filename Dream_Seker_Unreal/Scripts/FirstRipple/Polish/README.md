# First Ripple polish sources

The editable environment meshes and native material graphs are in `/Game/DreamSeeker/Levels/FirstRipple/Polish`. The `ripple-art-source` folder holds the final OBJ import sources, including UVs and the right-handed Y conversion expected by UE 5.8's Interchange OBJ importer.

The continuous shore and foliage are visual geometry. Swimming collision stays on the separate hidden riverbed, boundary guards and original fallen-willow collider; preserve those when editing scenery. Small decorations are instanced in nine groups rather than separate actors.

`BP_RhythmSwimmer.UpdateTimedLesson` advances the lesson stage once at X=2100, 4200, 7100 and 9200. The HUD uses the stage's entry time to fade its caption in and out. The first stage has two successive tips; later stages show one short tip each. Captions never stop movement or capture input. The H event has been retired.

`SwimmerVisual` owns the character proxy meshes, so its turning and kick motion do not rotate the camera or the collision capsule. `UpdateSwimVisual` updates the pose from aim direction and kick timing.

The original `/Game/Level_1_Learning` map remains preserved. This candidate uses `/Game/DreamSeeker/Levels/FirstRipple/LV_FirstRipple` through the first hub cloud.
