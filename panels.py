import bpy
import re
from . import rename_modules

class F_RENAME_PANEL_INFO():
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "F-Rename"



FUNC_OBJ = 'format_rename_object'
FUNC_BONE= 'format_rename_bone'


class F_RENAME_PT_object_rename(F_RENAME_PANEL_INFO,bpy.types.Panel):
    bl_label = ''
    bl_idname = "F_RENAME_PT_object_rename"
    @classmethod
    def poll(cls, context):
        return context.mode=='OBJECT'

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Rename Objects",icon='OBJECT_DATA')

    def draw(self, context):
        use_sel_order = "update_selected_objects_order" in [f.__name__ for f in bpy.app.handlers.depsgraph_update_post]
        scene = context.scene
        object_rename = scene.format_rename_object
        layout = self.layout

        row = layout.row(align=True)
        row.operator(f"{FUNC_OBJ}.show_all_name",text='Show all names',icon='HIDE_OFF').state = True
        row.operator(f"{FUNC_OBJ}.show_all_name",text='Hide all names',icon='HIDE_ON').state = False
        row = layout.row(align=True)
        icon_rename = 'TEMP' if use_sel_order else 'NONE'
        row.prop(object_rename,'rename_str',icon = icon_rename)
        row.operator(f"{FUNC_OBJ}.format_helper",text='',icon='INFO')
        row.operator(f"{FUNC_OBJ}.rename_preference",text='',icon='SOLO_ON')
        
        row = layout.row()
        
        row.operator(f"{FUNC_OBJ}.remove_prefix",text='->')#.is_delete_frist=True
        row.operator(f"{FUNC_OBJ}.add_prefix",text='+<')
        row.operator(f"{FUNC_OBJ}.rename",text='Rename')
        row.operator(f"{FUNC_OBJ}.add_suffix",text='>+')
        row.operator(f"{FUNC_OBJ}.remove_suffix",text='<-')#.is_delete_frist=False
        
        layout.separator(factor=1.0,type='LINE')


        # Operators
        box = layout.box()
        if not use_sel_order:
            box.operator(f"{FUNC_OBJ}.select_order_toggle",text='Active Select Order',icon='TEMP').state=True
        else:
            box.operator(f"{FUNC_OBJ}.select_order_toggle",text='Close Select Order',icon='PANEL_CLOSE',depress=True).state=False
            row_selOrder = box.row(align=True)
            sel_len = str(len(scene.get('ObjSelectOrder',[])))
            row_selOrder.label(text=f'Items : {sel_len}')
            
            row_selOrder.operator(f"{FUNC_OBJ}.set_team",text='A').teamID='A'
            row_selOrder.operator(f"{FUNC_OBJ}.set_team",text='B').teamID='B'

        
        box.separator(factor=1.0,type='LINE')
        
        col = box.column()
        if not use_sel_order:
            col.operator(f"{FUNC_OBJ}.copy_to_others",text='Copy Active to Others',icon='COPYDOWN')
            col.operator(f"{FUNC_OBJ}.swap_name",text='Swap Two Names',icon='FILE_REFRESH')
        else:
            col.operator(f"{FUNC_OBJ}.swap_list_rotation",text='Swap by list rotation',icon='FILE_REFRESH')
            col.operator(f"{FUNC_OBJ}.copy_to_others",text='Copy Active to Others',icon='COPYDOWN')
            col.operator(f"{FUNC_OBJ}.copy_a_to_b",text='Copy A to B',icon='COPYDOWN')
            col.operator(f"{FUNC_OBJ}.swap_a_and_b",text='Swap A & B',icon='AREA_SWAP')
            
        
        
        box.separator(factor=1.0,type='LINE')
        col = box.column()
        col.operator(f"{FUNC_OBJ}.copy_to_data",text='Copy Object Name To Data',icon='MESH_DATA')

# [ BONE ]
class F_RENAME_PT_bone_rename( F_RENAME_PANEL_INFO, bpy.types.Panel ):
    bl_idname = "F_RENAME_PT_Bone_Rename"
    bl_label = ""
    @classmethod
    def poll(cls, context):
        return context.mode in ['EDIT_ARMATURE','POSE']
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Rename Bones",icon='BONE_DATA')

    def draw(self, context):
        use_sel_order = "update_selected_bones_order" in [f.__name__ for f in bpy.app.handlers.depsgraph_update_post]
        Armature = context.object.data
        scene = context.scene   
        layout = self.layout

        # [Area] Rename Format String
        row = layout.row(align=True)
        row.alignment='RIGHT'
        row.label(text='Show Names')
        row.prop(Armature,'show_names',text='')

        row =layout.row(align=True)
        icon_rename = 'TEMP' if use_sel_order else 'NONE'
        row.prop(scene.format_rename_bone,'rename_str',icon=icon_rename)
        row.operator(f"{FUNC_BONE}.format_helper",text='',icon='INFO')


        row = layout.row()
        row.operator(f"{FUNC_BONE}.remove_prefix",text='->')
        row.operator(f"{FUNC_BONE}.add_prefix",text='+<')
        row.operator(f"{FUNC_BONE}.rename",text='Rename')
        row.operator(f"{FUNC_BONE}.add_suffix",text='>+')
        row.operator(f"{FUNC_BONE}.remove_suffix",text='<-')

        layout.operator(f"{FUNC_BONE}.rename_by_bone_tree",text='Rename by Tree',icon='OUTLINER')

        # [Area] Select Order
        layout.separator(factor=1.0,type='LINE')
        box = layout.box()
        if not use_sel_order:
            box.operator(f"{FUNC_BONE}.select_order_toggle",text='Select Order',icon='TEMP').state=True
        else:
            row_selOrder = box.row(align=True)
            row_selOrder.operator(f"{FUNC_BONE}.select_order_toggle",text='Select Order',icon='PANEL_CLOSE',depress=True).state=False

            row_selOrder = box.row(align=True)
            sel_len = str(len(scene.get('BoneSelectOrder',[])))
            row_selOrder.label(text=f'Items : {sel_len}')
            
            row_selOrder.operator(f"{FUNC_BONE}.set_team",text='A').teamID='A'
            row_selOrder.operator(f"{FUNC_BONE}.set_team",text='B').teamID='B'
        box.separator(factor=1.0,type='LINE')

        # [Area] Rename Operator
        col = box.column()
        if not use_sel_order:
            col.operator(f"{FUNC_BONE}.copy_to_others",text='Copy Active to Others',icon='COPYDOWN')
            col.operator(f"{FUNC_BONE}.swap_name",text='Swap Two Names',icon='FILE_REFRESH')
        else:
            col.operator(f"{FUNC_BONE}.swap_list_rotation",text='Swap by list rotation',icon='FILE_REFRESH')
            col.operator(f"{FUNC_BONE}.copy_to_others",text='Copy Active to Others',icon='COPYDOWN')
            col.operator(f"{FUNC_BONE}.copy_a_to_b",text='Copy A to B',icon='COPYDOWN')
            col.operator(f"{FUNC_BONE}.swap_a_and_b",text='Swap A & B',icon='AREA_SWAP')

# [Sreach and Replace]
class F_RENAME_PT_replace(F_RENAME_PANEL_INFO):
        
    @staticmethod
    def Replace_draw(context,layout,Replace,rename_func_name,found_cost):
        if not Replace:
            col = layout.column(align=True)
            row = col.row()
            row.alignment = 'RIGHT'
            row.prop(Replace,'is_selected_only',text='Selected Only')
            return col
        # Select Detail
        col = layout.column(align=True)
        area_detail = col.row()
        split = area_detail.split(factor=0.45,align=True)
        pie_title = split.menu_pie()
        pie_title.alignment = 'RIGHT'
        pie_title.label(text = 'Select')

        pie_details = split.menu_pie()
        pie_details.alignment = 'LEFT'
        pie_details.prop(Replace,'is_selected_only',text='Selected Only')

        area_detail = col.row()
        split = area_detail.split(factor=0.45,align=True)
        pie_title = split.menu_pie()
        pie_title.alignment = 'RIGHT'
        pie_title.label(text = 'Pattern Flag')
        pie_details = split.menu_pie()

        pie_details.alignment = 'LEFT'
        pie_details.prop(Replace,'is_ascii_only',text='ASCII Only')
        pie_details.prop(Replace,'is_ignore_case',text='Ignore Case')
        
        enabled_btn = not found_cost in ['NONE','ERROR']
        # Search Area
        col = layout.column(align=True)
        col.prop(Replace,'replace_from',text='',icon='ZOOM_ALL')
        split = col.split(factor=0.6,align=True)
        split.enabled = enabled_btn
        split.separator()
        if getattr(Replace,'is_selected_only'):
            split.operator(f"{rename_func_name}.select_by_name",text='Filter',icon='FILTER')
        else:
            split.operator(f"{rename_func_name}.select_by_name",text='Select',icon='RESTRICT_SELECT_OFF')

        # Replace Area
        col = layout.column(align=True)
        col.prop(Replace,'replace_to',text='',icon='PASTEDOWN')
        split = col.split(factor=0.6,align=True)
        split.enabled = enabled_btn
        if found_cost == 'ERROR':
            pie_info = split.menu_pie()
            pie_info.alert=True
            pie_info.label(text=f'Compile ERROR')
        elif found_cost == 'NONE':
            split.label(text=f'Found: 0')
        else:
            split.label(text=f'Found: {found_cost}')
        
        split.operator(f"{rename_func_name}.replace_name",text='Replace',icon='IMPORT')
        return layout

class F_RENAME_PT_object_replace(F_RENAME_PT_replace,bpy.types.Panel):
    bl_label = "Find & Replace"
    bl_idname = "F_RENAME_PT_object_replace"
    bl_parent_id = "F_RENAME_PT_object_rename"
    #bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        Replace = context.scene.format_rename_replace
        is_use_selected = getattr(Replace,'is_selected_only')
        is_ascii_only =  getattr(Replace,'is_ascii_only')
        is_ignore_case = getattr(Replace,'is_ignore_case')
        #pattern_mode = getattr(Replace,'campile_flags')
        pattern_mode = re.NOFLAG
        if is_ascii_only :
            pattern_mode |=re.ASCII
        if is_ignore_case :
            pattern_mode |=re.IGNORECASE
        sreach_txt = getattr(Replace,'replace_from')
        select_list = context.selected_objects if is_use_selected else context.scene.objects
        found_cost = rename_modules.get_found_element_cost(select_list,sreach_txt,pattern_mode)

        layout = self.layout
        self.Replace_draw(context,layout,Replace,FUNC_OBJ,found_cost)
    
class F_RENAME_PT_Bone_replace(F_RENAME_PT_replace,bpy.types.Panel):
    bl_label = "Find & Replace"
    bl_idname = "F_RENAME_PT_Bone_replace"
    bl_parent_id = "F_RENAME_PT_Bone_Rename"
    #bl_options = {"DEFAULT_CLOSED"}
    @staticmethod
    def get_bone_list(context,is_use_selected):
        def get_selected_bones(context):
            if context.mode == 'POSE': 
                return context.selected_pose_bones
            if context.mode == 'EDIT_ARMATURE': 
                return context.selected_editable_bones
            return []
        def get_data_bones(context):
            if context.mode == 'POSE': 
                return context.object.data.bones
            if context.mode == 'EDIT_ARMATURE': 
                return context.object.data.edit_bones
            return []
        return get_selected_bones(context) if is_use_selected else get_data_bones(context)
        
    def draw(self, context):
        Replace = context.scene.format_rename_replace
        is_use_selected = getattr(Replace,'is_selected_only')
        is_ascii_only =  getattr(Replace,'is_ascii_only')
        is_ignore_case = getattr(Replace,'is_ignore_case')
        #pattern_mode = getattr(Replace,'campile_flags')
        pattern_mode = re.NOFLAG
        if is_ascii_only :
            pattern_mode |=re.ASCII
        if is_ignore_case :
            pattern_mode |=re.IGNORECASE
        sreach_txt = getattr(Replace,'replace_from')
        select_list = self.get_bone_list(context,is_use_selected)

        found_cost = rename_modules.get_found_element_cost(select_list,sreach_txt,pattern_mode)

        layout = self.layout
        self.Replace_draw(context, layout,Replace,FUNC_BONE,found_cost)
        
        return None



classes_select_order = [ 
    ]


classes_rename = [ 
    F_RENAME_PT_object_rename,
    F_RENAME_PT_object_replace,
    F_RENAME_PT_bone_rename,
    F_RENAME_PT_Bone_replace
    ]


# [ Register ]
def register():
    for cls in classes_select_order:
        bpy.utils.register_class(cls)
    for cls in classes_rename:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes_rename:
        bpy.utils.unregister_class(cls)
    for cls in classes_select_order:
        bpy.utils.unregister_class(cls)
    
