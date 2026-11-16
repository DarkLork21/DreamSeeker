import unreal,random
A=unreal.EditorAssetLibrary;L=unreal.BlueprintEditorLibrary;random.seed(52)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ROOT='/Game/DreamSeeker/Levels/FirstRipple'
assert levels.load_level(ROOT+'/LV_FirstRipple')
soil=A.load_asset(ROOT+'/Materials/M_Silt');sphere=A.load_asset('/Engine/BasicShapes/Sphere')
green=A.load_asset(ROOT+'/Materials/M_ReedGreen')
for a in actors.get_all_level_actors():
    label=a.get_actor_label()
    if label.startswith('Water grass'):a.static_mesh_component.set_material(0,None)
    if label=='Visible riverbed':a.set_actor_hidden_in_game(True)
    if label.startswith('Willow canopy'):
        old=a.get_actor_location();a.set_actor_location(old+unreal.Vector(0,-200,100),False,False)
        a.set_actor_scale3d(unreal.Vector(3.8,2.0,1.2))
for i in range(29):
    x=-1300+i*460
    for y,z,sx,sy,sz,label in ((-1080,-130,7,7,2.0,'Natural shoreline'),(-350,-570,5.8,16,1.05,'Silt bed')):
        a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x,y,z+random.uniform(-12,12)))
        a.set_actor_label(label+' '+str(i));a.set_folder_path(unreal.Name('First Ripple / Shoreline'))
        c=a.static_mesh_component;c.set_static_mesh(sphere);c.set_material(0,soil);c.set_collision_profile_name('NoCollision');a.set_actor_scale3d(unreal.Vector(sx,sy,sz))
# Smaller foliage clusters keep the willow silhouette from reading as large spheres.
for i in range(65):
    x=random.uniform(-1700,700);y=random.uniform(-1280,-800);z=1250+150*__import__('math').sin(x/500)+random.uniform(-100,120)
    a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x,y,z));a.set_actor_label('Willow leaf cluster '+str(i));a.set_folder_path(unreal.Name('First Ripple / Willow'))
    c=a.static_mesh_component;c.set_static_mesh(sphere);c.set_material(0,green);c.set_collision_profile_name('NoCollision');a.set_actor_scale3d(unreal.Vector(random.uniform(.8,1.7),.7,.45))
assert levels.save_current_level()
bp=A.load_asset('/Game/DreamSeeker/Swimming/BP_RhythmSwimmer')
sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);data=unreal.SubobjectDataBlueprintFunctionLibrary
for h in sub.k2_gather_subobject_data_for_blueprint(bp):
    obj=data.get_object_for_blueprint(data.get_data(h),bp)
    if isinstance(obj,unreal.CameraComponent):
        obj.set_editor_property('projection_mode',unreal.CameraProjectionMode.PERSPECTIVE)
        obj.set_editor_property('relative_location',unreal.Vector(280,3200,650))
        obj.set_editor_property('relative_rotation',unreal.Rotator(0,-8,-90));obj.set_editor_property('field_of_view',50)
L.compile_blueprint(bp);assert A.save_loaded_asset(bp,False)
unreal.log('FIRST_RIPPLE_SCENERY_REFINED')
