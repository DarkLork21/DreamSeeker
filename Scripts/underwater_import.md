# Underwater World integration

The UE 4.20 source project is retained at `Dream_Seker_Unreal/UE_4.20_Underwater_World_v1.0/` and excluded from Git to avoid storing the pack twice.

The active import is `Dream_Seker_Unreal/Content/Underwater_1/`. Its original `/Game/Underwater_1` package paths are preserved. All 308 packages were resaved using Unreal Engine 5.8.2 ResavePackages, with zero conversion errors. No source project configuration or disabled UGridPlugin dependency was copied into Dream Seeker.

Open these levels from the Content Browser:

- `/Game/Underwater_1/Maps/Demonstration`
- `/Game/Underwater_1/Maps/Overview`

## Repeat the load/reference check

Run `Scripts/validate_underwater.py` through Unreal's PythonScript commandlet. It checks asset count, loads each asset, and checks hard and soft project package dependencies. The JSON result is written to `Dream_Seker_Unreal/Saved/UnderwaterValidation.json`.

For restricted automation sessions, use a project-local derived-data cache, a project-local `-ShaderWorkingDir`, and `-SCCProvider=None`. These overrides are for the validation process; they do not change the project's renderer settings.

## Version control

The existing `.gitattributes` tracks `.uasset` and `.umap` through Git LFS. Git LFS 3.7.1, global clean/smudge/process filters, and the repository's LFS pre-push hook were verified. Repository-local `git lfs install --local` was blocked by read-only access to `.git/config`; the existing filters and hook remain available. Nothing was committed or pushed during integration.

## Verification result (2026-10-27)

- Unreal 5.8.2 converted and successfully saved all 308 packages.
- Load/reference check passed: 301 StaticMesh, 2 Material, 1 Texture2D, 2 World, and 2 MapBuildDataRegistry assets. No failed loads or missing project dependencies.
- Full editor D3D12/SM6 rendering was checked on the AMD Radeon RX 6750 GRE. The Demonstration map was captured after Unreal finished asset/shader compilation, and its image was visually inspected. No missing-material checkerboards or material compile failures were observed.
- Capture: `Dream_Seker_Unreal/Saved/Screenshots/Underwater_Demonstration.png` (local generated evidence, ignored by Git).
- Unreal's original Git source-control provider setting was restored after validation. SSL/telemetry warnings from the restricted session did not prevent import or rendering.
- The existing project renderer settings and default level remain unchanged. The pack supplies scene assets and demonstration levels; this integration does not add gameplay or a water simulation system.
