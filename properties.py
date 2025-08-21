import bpy

'''
campile_flags_items=[
            ('0','NOFLAG','no flag','NONE',0),
            ('1','ASCII','ASCII-only matching','EVENT_A',1), 
            ('2','IGNORECASE','ignore case','EVENT_I',2),
            #('3','LOCALE','locale dependent','EVENT_L',3), 依賴本地語言不可靠
            #('4','MULTILINE','multi-line','EVENT_M',4), 無法換行故此模式無意義
            #('5','DOTALL','dot matches all','EVENT_S',5), 無換行符故此模式無意義
            #('6','UNICODE','Unicode matching','EVENT_U',6), 此標誌是多餘的，沒有任何作用
            #('7','VERBOSE','verbose','EVENT_X',7), 無法換行使此模式難以使用
                ]
'''


# -Object
class F_RENAME_PR_object_rename(bpy.types.PropertyGroup):
    # [ Rename String ]
    rename_str : bpy.props.StringProperty(name='',default='')

    # [ Format Rename Preference ]
    rep_mesh : bpy.props.StringProperty(default='MESH')
    rep_armature : bpy.props.StringProperty(default='ARMATURE')
    rep_camera : bpy.props.StringProperty(default='CAMERA')
    rep_curve : bpy.props.StringProperty(default='CURVE')
    rep_curves : bpy.props.StringProperty(default='CURVES')
    rep_surface : bpy.props.StringProperty(default='SURFACE')
    rep_meta : bpy.props.StringProperty(default='META')
    rep_font : bpy.props.StringProperty(default='FONT')
    rep_volume : bpy.props.StringProperty(default='VOLUME')
    rep_gpencil : bpy.props.StringProperty(default='GPENCIL')
    rep_speaker : bpy.props.StringProperty(default='SPEAKER')
    rep_pointcloud : bpy.props.StringProperty(default='POINTCLOUD')
    rep_lattice : bpy.props.StringProperty(default='LATTICE')
    
    #Empty
    use_image_name :bpy.props.BoolProperty(default=False)
    use_instance_name :bpy.props.BoolProperty(default=False)
    rep_emp_plain_axes : bpy.props.StringProperty(default='EMPTY')
    rep_emp_arrows : bpy.props.StringProperty(default='EMPTY')
    rep_emp_single_arrow : bpy.props.StringProperty(default='EMPTY')
    rep_emp_circle : bpy.props.StringProperty(default='EMPTY')
    rep_emp_cube : bpy.props.StringProperty(default='EMPTY')
    rep_emp_sphere : bpy.props.StringProperty(default='EMPTY')
    rep_emp_cone : bpy.props.StringProperty(default='EMPTY')
    rep_emp_image : bpy.props.StringProperty(default='IMAGE')
    rep_emp_instance : bpy.props.StringProperty(default='INSTANCE')

    #Force Field
    rep_frc_bold : bpy.props.StringProperty(default='BOLD')
    rep_frc_charge : bpy.props.StringProperty(default='CHARGE')
    rep_frc_curve_guide : bpy.props.StringProperty(default='CURVE_GUIDE')
    rep_frc_drag : bpy.props.StringProperty(default='DRAG')
    rep_frc_fluid_flow : bpy.props.StringProperty(default='FLUID_FLOW')
    rep_frc_force : bpy.props.StringProperty(default='FORCE')
    rep_frc_harmonic : bpy.props.StringProperty(default='HARMONIC')
    rep_frc_lennard_jones : bpy.props.StringProperty(default='LENNARD_JONES')
    rep_frc_magnetic : bpy.props.StringProperty(default='MAGNETIC')
    rep_frc_texture : bpy.props.StringProperty(default='TEXTURE')
    rep_frc_turbulence : bpy.props.StringProperty(default='TURBULENCE')
    rep_frc_vortex : bpy.props.StringProperty(default='VORTEX')
    rep_frc_wind : bpy.props.StringProperty(default='WIND')

    #Light
    rep_light_point : bpy.props.StringProperty(default='LIGHT')
    rep_light_sun   : bpy.props.StringProperty(default='LIGHT')
    rep_light_spot  : bpy.props.StringProperty(default='LIGHT')
    rep_light_area  : bpy.props.StringProperty(default='LIGHT')

    #Light_probe
    rep_probe_volume : bpy.props.StringProperty(default='LIGHT_PROBE')
    rep_probe_sphere : bpy.props.StringProperty(default='LIGHT_PROBE')
    rep_probe_plane : bpy.props.StringProperty(default='LIGHT_PROBE')


# - Bone
class F_RENAME_PR_bone_rename(bpy.types.PropertyGroup):
    rename_str : bpy.props.StringProperty(name='')

# - Bone
class F_RENAME_PR_replace(bpy.types.PropertyGroup):
    is_selected_only : bpy.props.BoolProperty(default=False)
    is_ascii_only : bpy.props.BoolProperty(default=False)
    is_ignore_case : bpy.props.BoolProperty(default=False)
    replace_from : bpy.props.StringProperty(default='')
    replace_to : bpy.props.StringProperty(default='')

class_list=[
    F_RENAME_PR_object_rename,
    F_RENAME_PR_bone_rename,
    F_RENAME_PR_replace
]
# [ Register ]
def register():
    for cls in class_list:
        bpy.utils.register_class(cls)
    bpy.types.Scene.format_rename_object = bpy.props.PointerProperty(type= F_RENAME_PR_object_rename)
    bpy.types.Scene.format_rename_bone = bpy.props.PointerProperty(type= F_RENAME_PR_object_rename)
    bpy.types.Scene.format_rename_replace = bpy.props.PointerProperty(type= F_RENAME_PR_replace)
def unregister():
    del bpy.types.Scene.format_rename_object
    del bpy.types.Scene.format_rename_bone
    del bpy.types.Scene.format_rename_replace

    class_list.reverse()
    for cls in class_list:
        bpy.utils.unregister_class(cls)   