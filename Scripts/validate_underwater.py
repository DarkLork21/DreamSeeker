import json
from pathlib import Path
import unreal

root = '/Game/Underwater_1'
registry = unreal.AssetRegistryHelpers.get_asset_registry()
registry.scan_paths_synchronous([root], force_rescan=True)
assets = registry.get_assets_by_path(root, recursive=True)
report = {'root': root, 'asset_count': len(assets), 'classes': {}, 'failed_loads': [], 'missing_dependencies': []}
options = unreal.AssetRegistryDependencyOptions(include_soft_package_references=True, include_hard_package_references=True)
for data in assets:
    path = str(data.package_name)
    kind = str(data.asset_class_path.asset_name)
    report['classes'][kind] = report['classes'].get(kind, 0) + 1
    if data.get_asset() is None:
        report['failed_loads'].append(path)
    for dependency in registry.get_dependencies(data.package_name, options):
        dependency = str(dependency)
        if dependency.startswith('/Game/') and not unreal.EditorAssetLibrary.does_asset_exist(dependency):
            report['missing_dependencies'].append({'asset': path, 'dependency': dependency})
report['passed'] = len(assets) == 308 and not report['failed_loads'] and not report['missing_dependencies']
output = Path(unreal.Paths.project_saved_dir()) / 'UnderwaterValidation.json'
output.write_text(json.dumps(report, indent=2))
unreal.log('UNDERWATER_VALIDATION ' + json.dumps(report))
if not report['passed']:
    raise RuntimeError('Underwater asset validation failed; inspect ' + str(output))
