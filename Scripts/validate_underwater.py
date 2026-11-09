"""Run with UE 5.8's PythonScript commandlet and -AllowCommandletRendering."""
import json
from pathlib import Path
import unreal

root = '/Game/Underwater_1'
registry = unreal.AssetRegistryHelpers.get_asset_registry()
registry.scan_paths_synchronous([root], True)
assets = registry.get_assets_by_path(root, recursive=True)
report = {'root': root, 'asset_count': len(assets), 'classes': {},
          'failed_loads': [], 'missing_dependencies': [], 'maps': [], 'materials': []}
options = unreal.AssetRegistryDependencyOptions(
    include_hard_package_references=True, include_soft_package_references=True)
for data in assets:
    name = str(data.package_name)
    kind = str(data.asset_class_path.asset_name)
    report['classes'][kind] = report['classes'].get(kind, 0) + 1
    asset = data.get_asset()
    if not asset:
        report['failed_loads'].append(name)
    if kind == 'World':
        report['maps'].append(name)
    if kind == 'Material' and asset:
        unreal.MaterialEditingLibrary.recompile_material(asset)
        report['materials'].append(name)
    for dep in registry.get_dependencies(data.package_name, options):
        dep = str(dep)
        if dep.startswith('/Game/') and not unreal.EditorAssetLibrary.does_asset_exist(dep):
            report['missing_dependencies'].append({'asset': name, 'dependency': dep})
report['map_loads'] = {}
for name in report['maps']:
    report['map_loads'][name] = bool(unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(name))
report['passed'] = (len(assets) == 308 and all(report['map_loads'].values()) and not report['failed_loads']
                    and not report['missing_dependencies'])
output = Path(unreal.Paths.project_saved_dir()) / 'UnderwaterValidation_Current.json'
output.write_text(json.dumps(report, indent=2))
if not report['passed']:
    raise RuntimeError('Underwater asset validation failed: ' + str(output))
