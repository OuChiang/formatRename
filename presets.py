import bpy
from bl_operators.presets import AddPresetBase

# [ Presets ]

# porp_id : [label ,icon , default]
rep_main_objs = {
    'rep_mesh' : ['Mesh','OUTLINER_OB_MESH','MESH'],
    'rep_armature' : ['Armature','OUTLINER_OB_ARMATURE','ARMATURE'],
    'rep_camera' : ['Camera','OUTLINER_OB_CAMERA','CAMERA'],
    'rep_curve' : ['Curve','OUTLINER_OB_CURVE','CURVE'],
    'rep_curves' : ['Fur','OUTLINER_OB_CURVES','CURVES'],
    'rep_surface' : ['Surface','OUTLINER_OB_SURFACE','SURFACE'],
    'rep_meta' : ['MetaBall','OUTLINER_OB_META','META'],
    'rep_font' : ['Font','OUTLINER_OB_FONT','FONT'],
    'rep_volume' : ['Volume','OUTLINER_OB_VOLUME','VOLUME'],
    'rep_gpencil' : ['GPencil','GP_SELECT_STROKES','GPENCIL'],
    'rep_speaker' : ['Speaker','OUTLINER_OB_SPEAKER','SPEAKER'],
    'rep_pointcloud' : ['PointCloud','OUTLINER_OB_POINTCLOUD','POINTCLOUD'],
    'rep_lattice' : ['Lattice','OUTLINER_OB_LATTICE','LATTICE'],
}
rep_empties = {
    #Empty
    'rep_emp_plain_axes' : ['Plain Axes','EMPTY_AXIS','EMPTY'],
    'rep_emp_arrows' : ['Arrows','EMPTY_ARROWS','EMPTY'],
    'rep_emp_single_arrow' : ['Single Arrow','EMPTY_SINGLE_ARROW','EMPTY'],
    'rep_emp_circle' : ['Circle','MESH_CIRCLE','EMPTY'],
    'rep_emp_cube' : ['Cube','CUBE','EMPTY'],
    'rep_emp_sphere' : ['Sphere','SPHERE','EMPTY'],
    'rep_emp_cone' : ['Cone','CONE','EMPTY'],
}
rep_instances = {
    'rep_emp_image' : ['Image','OUTLINER_OB_IMAGE','IMAGE'],
    'rep_emp_instance' : ['Instance','OUTLINER_OB_GROUP_INSTANCE','INSTANCE'],
}

rep_froces = {
    #Force Field
    'rep_frc_bold' : ['BOLD','FORCE_BOID','BOLD'],
    'rep_frc_charge' : ['CHARGE','FORCE_CHARGE','CHARGE'],
    'rep_frc_curve_guide' : ['FORCE_CURVE','FORCE_CURVE','FORCE_CURVE'],
    'rep_frc_drag' : ['DRAG','FORCE_DRAG','DRAG'],
    'rep_frc_fluid_flow' : ['FLUIDFLOW','FORCE_FLUIDFLOW','FLUIDFLOW'],
    'rep_frc_force' : ['FORCE','FORCE_FORCE','FORCE'],
    'rep_frc_harmonic' : ['HARMONIC','FORCE_HARMONIC','HARMONIC'],
    'rep_frc_lennard_jones' : ['LENNARDJONES','FORCE_LENNARDJONES','LENNARDJONES'],
    'rep_frc_magnetic' : ['MAGNETIC','FORCE_MAGNETIC','MAGNETIC'],
    'rep_frc_texture' : ['TEXTURE','FORCE_TEXTURE','TEXTURE'],
    'rep_frc_turbulence' : ['TURBULENCE','FORCE_TURBULENCE','TURBULENCE'],
    'rep_frc_vortex' : ['VORTEX','FORCE_VORTEX','VORTEX'],
    'rep_frc_wind' : ['WIND','FORCE_WIND','WIND'],

}
rep_lights = {
    #Light
    'rep_light_point' : ['Point','LIGHT_POINT','LIGHT'],
    'rep_light_sun'   : ['Sun','LIGHT_SUN','LIGHT'],
    'rep_light_spot'  : ['Spot','LIGHT_SPOT','LIGHT'],
    'rep_light_area'  : ['Area','LIGHT_AREA','LIGHT'],
}
rep_lights_probe = {
    #Light_probe
    'rep_probe_volume' : ['Volume','LIGHTPROBE_VOLUME','LIGHT_PROBE'],
    'rep_probe_sphere' : ['Sphere','LIGHTPROBE_SPHERE','LIGHT_PROBE'],
    'rep_probe_plane' : ['Plane','LIGHTPROBE_PLANE','LIGHT_PROBE']
}
props_list=[
    rep_main_objs,
    rep_empties,
    rep_instances,
    rep_froces,
    rep_lights,
    rep_lights_probe
]
class F_RENAME_OBJ_OT_Rename_Preferences_Reset(bpy.types.Operator):
    """Rename Preferences Reset"""
    bl_idname = "format_rename_object.rename_preference_reset"
    bl_label = "Rename Preferences Reset"

    def execute(self, context):
        object_rename = context.scene.format_rename_object
        
        for i in props_list:
            for key,val in i.items():
                setattr(object_rename,key,val[2])
        setattr(object_rename,'use_image_name',False)
        setattr(object_rename,'use_instance_name',False)
        return {'FINISHED'}

class F_RENAME_OBJ_OT_Rename_Preferences(bpy.types.Operator):
    """Replace Custom Type Settings"""
    bl_idname = "format_rename_object.rename_preference"
    bl_label = "Rename Preferences"
    replace_tab : bpy.props.EnumProperty(
        items =[
            ('0','Object','','OUTLINER_OB_MESH',0),
            ('1','Empty','','OUTLINER_OB_EMPTY',1),
            ('2','Light','','OUTLINER_OB_LIGHT',2),
                ]
    )

    def execute(self, context):
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self)#,width=500)

    def draw(self, context):
        object_rename = context.scene.format_rename_object
        # Use Simple Mode
        layout = self.layout
        top_bar = layout.row(align=True)
       
        # Tab
        row = layout.row(align=True)
        row.menu(F_RENAME_OBJ_MT_Palette_Preset.__name__,text =F_RENAME_OBJ_MT_Palette_Preset.bl_label)
        row.operator(F_RENAME_OBJ_OT_Palette_Preset.bl_idname, text="", icon='ZOOM_IN')
        row.operator(F_RENAME_OBJ_OT_Palette_Preset.bl_idname, text="", icon='ZOOM_OUT').remove_active = True
        row.operator("format_rename_object.rename_preference_reset",text="", icon='FILE_REFRESH')

        layout.prop_tabs_enum(self,'replace_tab')
        tab_id = getattr(self,'replace_tab')

        def tab_objs(layout,obj_dict):
            for key,val in obj_dict.items():
                split = layout.split(factor=0.5)
                split.label(text=val[0],icon=val[1])
                split.prop(object_rename,key,text='',icon='NONE')
        def title_bar(layout,text):
            row = layout.row(align=True)
            pie = row.menu_pie()
            pie.alignment='CENTER'
            pie.label(text=text)
        if tab_id=='0':
            tab_objs(layout,rep_main_objs)
        if tab_id=='1':
            title_bar(layout,'Empty')
            tab_objs(layout,rep_empties)  
            split = layout.split(factor=0.5)
            split.label(text='Image',icon='OUTLINER_OB_IMAGE')
            row = split.row(align=True)
            row.prop(object_rename,'use_image_name',text='',icon='OUTLINER_OB_IMAGE')
            if not getattr(object_rename,'use_image_name'):
                row.prop(object_rename,'rep_emp_image',text='',icon='NONE')
            # Instance Empty
            split = layout.split(factor=0.5)
            split.label(text='Instance',icon='OUTLINER_OB_GROUP_INSTANCE')
            row = split.row(align=True)
            row.prop(object_rename,'use_instance_name',text='',icon='OUTLINER_OB_GROUP_INSTANCE')
            if not getattr(object_rename,'use_instance_name'):
                row.prop(object_rename,'rep_emp_instance',text='',icon='NONE')

            title_bar(layout,'Force Field')
            tab_objs(layout,rep_froces)    
        if tab_id=='2':
            title_bar(layout,'Light')
            tab_objs(layout,rep_lights)    
            title_bar(layout,'Light Probe')
            tab_objs(layout,rep_lights_probe)    

class F_RENAME_OBJ_MT_Palette_Preset(bpy.types.Menu):
    bl_label = "Rename Replace Presets"
    preset_subdir = "scene/rename_replace"
    preset_operator = "script.execute_preset"
    draw = bpy.types.Menu.draw_preset

def preset_list():
    output_list = [f"replace_str.{j}" for i in props_list for j in i.keys()]
    output_list.append("replace_str.use_image_name")
    output_list.append("replace_str.use_instance_name")
    return output_list
class F_RENAME_OBJ_OT_Palette_Preset(AddPresetBase, bpy.types.Operator):
    """"Rename Replace Presets"""
    bl_idname = "format_rename_object.palette"
    bl_label = "Palette Presets"
    preset_menu = "F_RENAME_OBJ_MT_Palette_Preset"
    preset_defines = ["replace_str = bpy.context.scene.format_rename_object"]
    preset_values = preset_list()
    preset_subdir = "scene/rename_replace"


classes_rename = [ 
    F_RENAME_OBJ_MT_Palette_Preset,
    F_RENAME_OBJ_OT_Palette_Preset,
    F_RENAME_OBJ_OT_Rename_Preferences_Reset,
    F_RENAME_OBJ_OT_Rename_Preferences,
    ]


# [ Register ]
def register():
    for cls in classes_rename:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes_rename:
        bpy.utils.unregister_class(cls)
