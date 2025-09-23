import bpy
import re

from . import rename_modules

OBJ_SELECTED_ORDER = 'ObjSelectOrder'
OBJ_TEAM_A = 'obj_teamA'
OBJ_TEAM_B = 'obj_teamB'


def is_use_order():
    is_selection_update = any(
        h.__name__ == 'update_selected_objects_order'
        for h in bpy.app.handlers.depsgraph_update_post
    )
    return is_selection_update

# [ Select Order ] 
def get_objs(context):
    if is_use_order():
        return context.scene.get(OBJ_SELECTED_ORDER,[])
    return [o.name for o in context.selected_objects]


class F_RENAME_OBJ_OT_Show_All_Name_Toggle(bpy.types.Operator):
    """Show all objects names """
    bl_idname = "format_rename_object.show_all_name"
    bl_label = "Use Select Order Toggle"
    state :  bpy.props.BoolProperty( default=True )
    
    def execute(self, context):
        objs = bpy.data.objects
        for obj in objs:
            obj.show_name = self.state

        return {'FINISHED'}

class F_RENAME_OBJ_OT_Select_Order_Toggle(bpy.types.Operator):
    """Recode order when object select"""
    bl_idname = "format_rename_object.select_order_toggle"
    bl_label = "Use Select Order Toggle"
    state :  bpy.props.BoolProperty( default=True )
    
    def execute(self, context):
        context.scene[OBJ_SELECTED_ORDER] = []
        def update_selected_objects_order(scene):
            # Check 
            if bpy.context.mode != "OBJECT":
                return
            
            is_selection_update = any(
                not u.is_updated_geometry
                and not u.is_updated_transform
                and not u.is_updated_shading
                for u in context.view_layer.depsgraph.updates
            )

            if is_selection_update:
                # get order list
                orderList = context.scene.get(OBJ_SELECTED_ORDER,[])
                
                # get selected list
                selected = [obj.name for obj in context.selected_objects[:]]
                
                # remove deselect
                orderList = [ obj for obj in orderList if obj in selected ]
                
                # append new select
                for obj in selected[:]:
                    if obj not in orderList:
                        orderList.append(obj)
                        
                context.scene[OBJ_SELECTED_ORDER] = orderList
                
        # Trun On
        if self.state:
            bpy.app.handlers.depsgraph_update_post.append(update_selected_objects_order)
            bpy.ops.object.select_all(action='DESELECT')
            self.report({'INFO'}, '[Format Rename]: Object Select Order - Trun On')
        # Trun Off
        else :
            for teamName in [OBJ_SELECTED_ORDER, OBJ_TEAM_A, OBJ_TEAM_B]:
                team = context.scene.get(teamName,None)
                if team:
                    del team
            for f in bpy.app.handlers.depsgraph_update_post:
                if f.__name__ == "update_selected_objects_order":
                    bpy.app.handlers.depsgraph_update_post.remove(f)
            self.report({'INFO'}, '[Format Rename]: Object Select Order - Trun Off')
        return {'FINISHED'}

class F_RENAME_OBJ_OT_Set_Team(bpy.types.Operator):
    """Set selected objects to team"""
    bl_idname = "format_rename_object.set_team"
    bl_label = "Object Set Team"
    teamID : bpy.props.StringProperty( default='A' )
    @classmethod
    def poll(cls, context):
        return context.scene.get(OBJ_SELECTED_ORDER,False)
    
    def execute(self, context):
        context.scene[f'obj_team{self.teamID}'] = context.scene.get(OBJ_SELECTED_ORDER)
        self.report(type={'INFO'} ,message =f'[Format Rename]: Object Team{self.teamID} Updated')
        return {'FINISHED'}


# [ Rename ]
class Rename_Operator_Root:
    @staticmethod
    def replace_pref_word(data,obj):
        if obj.type == 'EMPTY':
            ## Type Order : Force -> Instance -> Image -> Shape
            # force field
            if obj.field :
                Type = obj.field.type.lower()
                return getattr(data,f'rep_frc_{Type}')
            # instance collection
            if obj.instance_type =='COLLECTION' :
                if getattr(data,'use_instance_name'):
                    return obj.instance_collection.name
                return getattr(data,'rep_emp_instance')
            # image
            if obj.empty_display_type == 'IMAGE':
                if getattr(data,'use_image_name'):
                    return obj.data.name
            # shpae
            word = obj.empty_display_type.lower()
            return getattr(data,f'rep_emp_{word}')
        
        if obj.type == 'LIGHT':
            word = obj.data.type.lower()
            return getattr(data,f'rep_light_{word}')
        if obj.type == 'LIGHT_PROBE':
            word = obj.data.type.lower()
            return getattr(data,f'rep_probe_{word}')
        if obj.type == 'GREASEPENCIL':
            return getattr(data,'rep_gpencil')
        return getattr(data,f'rep_{obj.type.lower()}','')
    def word_replace(self,context,obj,fromat_str,digits,order,active_name):
        # order : {a} {A} {Aa} {-Aa} {AA} {-AA} {aa} {-aa} 
        fromat_str = rename_modules.rename_format_to_abc(fromat_str,order)

        #// Index : {i} {i,start} {i,start,digital}
        #//fromat_str = rename_modules.rename_format_to_index(fromat_str,order,digits)

        # Index : {###}
        fromat_str = rename_modules.rename_format_to_number(fromat_str,order)

        # Relationship
        if "{self}" in fromat_str:
            fromat_str = fromat_str.replace("{self}",obj.name)
        if "{data}" in fromat_str:
            data_name = obj.data.name if obj.data else ''
            fromat_str = fromat_str.replace("{data}",data_name)
        if "{parent}" in fromat_str:
            pt = obj.parent
            pt_name = pt.name if pt else ""
            fromat_str = fromat_str.replace("{parent}",pt_name)
        if "{active}" in fromat_str:
            fromat_str = fromat_str.replace("{active}",active_name)
        if "{scene}" in fromat_str:
            fromat_str = fromat_str.replace("{scene}",context.scene.name)
        if "{view_layer}" in fromat_str:
            fromat_str = fromat_str.replace("{view_layer}",context.view_layer.name)
        
        # Type
        if "{TYPE}" in fromat_str:
            fromat_str = fromat_str.replace("{TYPE}",obj.type) 
        if "{Type}" in fromat_str:
            fromat_str = fromat_str.replace("{Type}",obj.type.capitalize())  
        if "{type}" in fromat_str:
            fromat_str = fromat_str.replace("{type}",obj.type.lower()) 
        if "{pref}" in fromat_str:
            object_rename = context.scene.format_rename_object
            fromat_str = fromat_str.replace("{pref}",self.replace_pref_word(object_rename,obj)) 
        return fromat_str
    
    def exe_rename(self, context,func_rename):
        object_rename = context.scene.format_rename_object
        fromat_str = getattr(object_rename,'rename_str')
        use_order = is_use_order()
        objs = get_objs(context)

        digits = len(str(len(objs)))
        newList = []
        active_object_name = context.object.name
        for i,old_name in enumerate(objs):
            Obj = bpy.data.objects[old_name]
            replaced_str = self.word_replace(context,Obj,fromat_str,digits,i,active_object_name)
            func_rename(Obj,replaced_str)
            newList.append(Obj.name)
        if use_order:
            context.scene[OBJ_SELECTED_ORDER] = newList
        self.report(type={'INFO'} ,message =f'[Format Rename]: {str(len(objs))} Objects Renamed')

class F_RENAME_OBJ_OT_Rename(Rename_Operator_Root,bpy.types.Operator):
    """Format rename objects"""
    bl_idname = "format_rename_object.rename"
    bl_label = "Rename"
    
    def execute(self, context):
        func_rename = lambda obj,replaced_str: setattr(obj,'name',replaced_str)
        self.exe_rename(context,func_rename)
        return {'FINISHED'}

class F_RENAME_OBJ_OT_Add_Prefix(Rename_Operator_Root,bpy.types.Operator):
    """Add Prefix To Object Name"""
    bl_idname = "format_rename_object.add_prefix"
    bl_label = "Add Prefix"
    
    def execute(self, context):
        func_rename = lambda obj,replaced_str: setattr(obj,'name',replaced_str+obj.name)
        self.exe_rename(context,func_rename)
        return {'FINISHED'}

class F_RENAME_OBJ_OT_Add_Suffix(Rename_Operator_Root,bpy.types.Operator):
    """Add Suffix To Object Name"""
    bl_idname = "format_rename_object.add_suffix"
    bl_label = "Add Suffix"
    
    def execute(self, context):
        func_rename = lambda obj,replaced_str: setattr(obj,'name',obj.name+replaced_str)
        self.exe_rename(context,func_rename)
        return {'FINISHED'}

# [ Remove ]
def function_remove_words(self, context,func_del):
    objs = get_objs(context)
    newList = []
    for obj in objs:
        Obj = bpy.data.objects[obj]
        Obj.name = func_del(Obj)#Obj.name[1:] if self.is_delete_frist else Obj.name[:-1]
        newList.append(Obj.name)
    if is_use_order():
        context.scene[OBJ_SELECTED_ORDER] = newList
    self.report(type={'INFO'} ,message =f'[Format Rename]: {str(len(objs))} Objects Renamed')

class F_RENAME_OBJ_OT_Remove_Prefix(bpy.types.Operator):
    """Remove Object Name Frist Character"""
    bl_idname = "format_rename_object.remove_prefix"
    bl_label = "Remove Frist Character"
    is_delete_frist : bpy.props.BoolProperty(default=True)
    
    def execute(self, context):
        func_del = lambda Obj : Obj.name[1:]
        function_remove_words(self, context,func_del)
        return {'FINISHED'}
class F_RENAME_OBJ_OT_Remove_Suffix(bpy.types.Operator):
    """Remove Object Name Last Character"""
    bl_idname = "format_rename_object.remove_suffix"
    bl_label = "Remove Last Character"
    is_delete_frist : bpy.props.BoolProperty(default=True)
    
    def execute(self, context):
        func_del = lambda Obj : Obj.name[:-1]
        function_remove_words(self, context,func_del)
        return {'FINISHED'}
    
# Operators Simple
class F_RENAME_OBJ_OT_Copy_To_Others(bpy.types.Operator):
    """Copy active object name to other selected objects"""
    bl_idname = "format_rename_object.copy_to_others"
    bl_label = "Copy name"

    def execute(self, context):
        #ordered,objs = get_objs(context)
        objs = [o.name for o in context.selected_objects]

        act = context.active_object
        if not act:
            self.report(type={'ERROR'} ,message ='[Format Rename]: Copy need to specify an active object')
            return {'FINISHED'}
        newNm = act.name

        newList = []
        counter = 0
        for i in range(len(objs)):
            Obj = bpy.data.objects[objs[i]]
            oldNm = Obj.name
            if oldNm != act.name :
                Obj.name = f'{newNm}'
                newList.append(Obj.name)
                counter+=1
            else :
                newList.append(act.name)
        
        if is_use_order():
            context.scene[OBJ_SELECTED_ORDER] = newList
        self.report(type={'INFO'} ,message =f'[Format Rename]: {str(counter)} Objects Renamed')
        return {'FINISHED'}

class F_RENAME_OBJ_OT_Swap_Name(bpy.types.Operator):
    """Swap two object names"""
    bl_idname = "format_rename_object.swap_name"
    bl_label = "Switch Name"
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects)==2
    def execute(self, context):
        objs = context.selected_objects
        objA = objs[0].name
        objB = objs[1].name
        objs[0].name = objA+'Temp_Name_For_Exchange_Names'
        objs[1].name = objA
        objs[0].name = objB
        self.report(type={'INFO'} ,message =f'[Format Rename]: {objA} and {objB} swapped')
        return {'FINISHED'}


# Operators Order
class F_RENAME_OBJ_OT_Swap_List_Rotation(bpy.types.Operator):
    """Exchange object names by List Rotation
['A','B','C'] to ['C','A','B']"""
    bl_idname = "format_rename_object.swap_list_rotation"
    bl_label = "Switch Name"

    def execute(self, context):
        objs = context.scene.get(OBJ_SELECTED_ORDER,[])
        if not objs:
            return {'CANCELLED'}
        #objs.reverse()
        newList = []
        for i in range(1,len(objs)):
            objA = bpy.data.objects[objs[i-1]]
            objB = bpy.data.objects[objs[i]]
            objA.name = 'Temp_Name_For_Exchange_Names'
            objB.name = objs[i-1]
            objA.name = objs[i]
            newList.append(objA.name)
        context.scene[OBJ_SELECTED_ORDER] = newList
        self.report(type={'INFO'} ,message =f'[Format Rename]: {str(len(newList))} Objects Renamed')
        return {'FINISHED'}

# Operators Teams
class F_RENAME_OBJ_OT_Swap_A_And_B(bpy.types.Operator):
    """Exchange frist and second object's name
['A','B'] to ['B','A']"""
    bl_idname = "format_rename_object.swap_a_and_b"
    bl_label = "Switch A & B"
    @classmethod
    def poll(cls, context):
        return all(context.scene.get(name,None) for name in [OBJ_TEAM_A,OBJ_TEAM_B])
    def execute(self, context):
        teamA = context.scene.get(OBJ_TEAM_A,[])
        teamB = context.scene.get(OBJ_TEAM_B,[])
        newA = []
        newB = []
        for i in range(min(len(teamA),len(teamB))):
            objA = bpy.data.objects.get(teamA[i],None)
            objB = bpy.data.objects.get(teamB[i],None)
            if not all([objA,objB]):
                continue
            objA.name = 'Temp_Name_For_Exchange_Names'
            objB.name = teamA[i]
            objA.name = teamB[i]
            newA.append(objA.name)
            newB.append(objB.name)
        context.scene[OBJ_TEAM_A] = newA
        context.scene[OBJ_TEAM_B] = newB
        self.report(type={'INFO'} ,message =f'[Format Rename]: Swapped TeamA and TeamB')
        return {'FINISHED'}

    
class F_RENAME_OBJ_OT_Copy_A_To_B(bpy.types.Operator):
    """Copy A team's name to B team"""
    bl_idname = "format_rename_object.copy_a_to_b"
    bl_label = "Copy A & B"
    @classmethod
    def poll(cls, context):
        return all(context.scene.get(name,None) for name in [OBJ_TEAM_A,OBJ_TEAM_B])
    def execute(self, context):
        teamA = context.scene.get(OBJ_TEAM_A,[])
        teamB = context.scene.get(OBJ_TEAM_B,[])
        newList =[]
        for i in range(min(len(teamA),len(teamB))):
            objA = bpy.data.objects.get(teamA[i],None)
            objB = bpy.data.objects.get(teamB[i],None)
            if not all([objA,objB]):
                continue
            objB.name = teamA[i]+'.copyName'
            newList.append(objB.name)
        context.scene[OBJ_TEAM_B] = newList
        self.report(type={'INFO'} ,message =f'[Format Rename]: Copied TeamA to TeamB')
        return {'FINISHED'}
    

    
class F_RENAME_OBJ_OT_Copy_To_Data(bpy.types.Operator):
    """Copy object name to data"""
    bl_idname = "format_rename_object.copy_to_data"
    bl_label = "Fallow Data Name"
    
    def execute(self, context):
        Objects = context.selected_objects[:]
        for obj in Objects:
            if obj.type =='EMPTY':
                continue
            obj.data.name = obj.name
        self.report(type={'INFO'} ,message =f'[Format Rename]: Data Copied ')
        return {'FINISHED'}



# [Format Helper]
class F_RENAME_OBJ_OT_Format_Helper(bpy.types.Operator):
    """The penal for format information"""
    bl_idname = "format_rename_object.format_helper"
    bl_label = "Rename replace info"
    def execute(self, context):
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self,width=500)

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        def row_text(layout,btn_word,title,*args):
            sp = layout.split(factor=0.25)
            pie_title = sp.menu_pie()
            pie_title.alignment='LEFT'
            row_1 = pie_title.row()
            if btn_word:
                btn =row_1.operator("format_rename_object.copy_rename_format",text=title,icon='INFO')
                btn.format_word = btn_word
            else:
                row_1.label(text=title)
            for txt in args:
                pie_info = sp.menu_pie()
                pie_info.alignment='LEFT'
                pie_info.label(text=txt)
        row_text(col,None,'# Format','# Output','# Example')
        row_text(col,None,'Index')
        row_text(col,'{#}','{#..}',f'\"#\" number == digits, start from 1','{###} : 001,002,003...')
        row_text(col,'{#,1}','{#..,1}','start from number','{##,-1} : -01,00,01...')
        col.label(text='')
        row_text(col,None,'Abc')
        row_text(col,'{a}','{a}','a to z','a,b,c...')
        row_text(col,'{A}','{A}','A to Z','A,B,C...')
        row_text(col,'{Aa}','{Aa}','Bijective base-26 system','A,..,Z,Aa,Ab,...')
        row_text(col,'{-Aa}','{-Aa}','Reverse Bijective base-26 system','A,..,Z,Aa,Ba,...')
        row_text(col,'{AA}','{AA}','Bijective base-26 system','A,..,Z,AA,AB,...')
        row_text(col,'{-AA}','{-AA}','Reverse Bijective base-26 system','A,..,Z,AA,BA,...')
        
        col.label(text='')

        row_text(col,None,'Context')
        row_text(col,'{self}','{self}','Output Self Name','')
        row_text(col,'{data}','{data}','Output Data Name','')
        row_text(col,'{parent}','{parent}','Output Parent Name','')
        row_text(col,'{active}','{active}','Output Active Object Name','')
        row_text(col,'{scene}','{scene}','Output Active Scene Name','')
        row_text(col,'{view_layer}','{view_layer}','Output Active ViewLayer Name','')
        col.label(text='')

        row_text(col,None,'Type')
        row_text(col,'{TYPE}','{TYPE}','UpperCase','MESH / CAMERA / LIGHT')
        row_text(col,'{Type}','{Type}','Title Case','Mesh / Camera / Light')
        row_text(col,'{type}','{type}','Lowercase','mesh / camera / light')
        row_text(col,'{pref}','{pref}','Custom Preference Settings','')





class F_RENAME_OT_Copy_Rename_Format(bpy.types.Operator):
    """Copy rename format to clipboard"""
    bl_idname = "format_rename_object.copy_rename_format"
    bl_label = "Copy rename format words"
    format_word : bpy.props.StringProperty(
            default=''
    )
    def execute(self, context):
        context.window_manager.clipboard = self.format_word
        self.report(type={'INFO'} ,message =f'[Format Rename]: copied {self.format_word} to clipboard')
        return {'FINISHED'}


# [Replace]
class F_RENAME_OBJ_OT_Select_By_Name(bpy.types.Operator):
    """"Select By Object Name"""
    bl_idname = "format_rename_object.select_by_name"
    bl_label = "Select By Object Name"

    def execute(self, context):
        Replace = context.scene.format_rename_replace
        is_use_selected = getattr(Replace,'is_selected_only')
        is_ascii_only =  getattr(Replace,'is_ascii_only')
        is_ignore_case = getattr(Replace,'is_ignore_case')
        pattern_mode = re.NOFLAG
        if is_ascii_only :
            pattern_mode |=re.ASCII
        if is_ignore_case :
            pattern_mode |=re.IGNORECASE
        sreach_txt = getattr(Replace,'replace_from')
        old_list = context.selected_objects if is_use_selected else context.scene.objects
        new_list = rename_modules.re_filter_element(old_list,sreach_txt,pattern_mode)

        if not new_list:
            self.report(type={'WARNING'} ,message =f'[Format Rename]: Nothing Found')
            return {'FINISHED'}
        if new_list=='ERROR':
            self.report(type={'ERROR'} ,message =f'[Format Rename]: Sreach input error')
            return {'FINISHED'}
        
        bpy.ops.object.select_all(action='DESELECT')
        if not context.view_layer.objects.active in new_list:
            context.view_layer.objects.active = new_list[0]

        for obj in new_list:
            try :
                obj.select_set(state=True)
            except:
                pass
        
        return {'FINISHED'}
    
class F_RENAME_OBJ_OT_Replace_Name(bpy.types.Operator):
    """"Replace Object Name"""
    bl_idname = "format_rename_object.replace_name"
    bl_label = "Replace Object Name"

    def execute(self, context):
        Replace = context.scene.format_rename_replace
        is_use_selected = getattr(Replace,'is_selected_only')
        is_ascii_only =  getattr(Replace,'is_ascii_only')
        is_ignore_case = getattr(Replace,'is_ignore_case')
        sreach_txt = getattr(Replace,'replace_from')
        replace_txt =  getattr(Replace,'replace_to')

        pattern_mode = re.NOFLAG
        if is_ascii_only :
            pattern_mode |=re.ASCII
        if is_ignore_case :
            pattern_mode |=re.IGNORECASE
            
        Objects = context.selected_objects if is_use_selected else context.scene.objects
        rename_modules.rename_element(self,Objects,sreach_txt,replace_txt,pattern_mode)
        return {'FINISHED'}
    


classes_select_order = [ 
    F_RENAME_OBJ_OT_Select_Order_Toggle,
    F_RENAME_OBJ_OT_Set_Team,
    ]


classes_rename = [ 
    F_RENAME_OBJ_OT_Show_All_Name_Toggle,
    F_RENAME_OBJ_OT_Rename,
    F_RENAME_OBJ_OT_Add_Prefix,
    F_RENAME_OBJ_OT_Add_Suffix,
    F_RENAME_OBJ_OT_Format_Helper,
    F_RENAME_OBJ_OT_Remove_Prefix,
    F_RENAME_OBJ_OT_Remove_Suffix,
    F_RENAME_OBJ_OT_Swap_Name,
    F_RENAME_OBJ_OT_Swap_List_Rotation,
    F_RENAME_OBJ_OT_Swap_A_And_B,
    F_RENAME_OBJ_OT_Copy_To_Others,
    F_RENAME_OBJ_OT_Copy_A_To_B,
    F_RENAME_OBJ_OT_Copy_To_Data,
    F_RENAME_OBJ_OT_Select_By_Name,
    F_RENAME_OBJ_OT_Replace_Name,
    F_RENAME_OT_Copy_Rename_Format,
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
    