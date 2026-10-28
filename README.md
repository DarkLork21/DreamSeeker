# DreamSeeker
Git repository for Game design 2 project

## Underwater assets

Open `Dream_Seker_Unreal/Dream_Seker_Unreal.uproject` in Unreal Engine 5.8.
The imported pack is available in the Content Browser at `Content/Underwater_1`.
Its example levels are `Underwater_1/Maps/Demonstration` and
`Underwater_1/Maps/Overview`.

All 308 source asset files were copied from the existing nested
`UE_4.20_Underwater_World_v1.0/Content/Underwater_1` folder, retaining their
`/Game/Underwater_1` package paths. The nested source project is preserved;
use the main project above for development.

Validation on October 27, 2026 using UE 5.8.2 loaded 301 static meshes,
2 materials, 1 texture, 2 maps, and 2 map build-data assets. Both maps opened
and no missing project dependencies were found. The validation script is
`Scripts/validate_underwater.py`; it writes its result to the project's Saved
folder. No additional compatibility changes were required for asset loading.
The Demonstration map also passed the editor map check with zero errors or
warnings, and a fresh viewport capture was visually inspected for geometry
and material rendering. The screenshot is in
`Dream_Seker_Unreal/Saved/Screenshots/Underwater_Demonstration_Current.png`.

Git LFS is configured for `*.uasset` and `*.umap`. These local additions
must be staged and committed before they are part of Git history. Existing
history has not been rewritten or retroactively migrated to LFS.
