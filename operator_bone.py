import bpy
import re

from . import rename_modules


# [ OT ]
BONE_SELECTED_ORDER = 'BoneSelectOrder'
BONE_TEAM_A = 'bone_teamA'
BONE_TEAM_B = 'bone_teamB'
def get_selected_bones(context):
    if context.mode == 'POSE': 
        return context.selected_pose_bones
    if context.mode == 'EDIT_ARMATURE': 
        return context.selected_editable_bones

def get_data_bones(context):
    if context.mode == 'POSE': 
        return context.object.pose.bones
    if context.mode == 'EDIT_ARMATURE': 
        return context.object.data.edit_bones

def get_active_bone(context):
    if context.mode=='POSE':
        return context.active_pose_bone
    if context.mode=='EDIT_ARMATURE':
        return context.active_bone

def bone_deselect(context):
    if context.mode == 'POSE':
        bpy.ops.pose.select_all(action='DESELECT')
    if context.mode == 'EDIT_ARMATURE':
        bpy.ops.armature.select_all(action='DESELECT')


def is_use_order():
    is_selection_update = any(
        h.__name__ == 'update_selected_bones_order'
        for h in bpy.app.handlers.depsgraph_update_post
    )
    return is_selection_update


# [ Select Order ]
class F_RENAME_BONE_OT_Order_Toggle(bpy.types.Operator):
    """Trun on/off bone select order toggle"""
    bl_idname = "format_rename_bone.select_order_toggle"
    bl_label = "Use Select Order Toggle"
    state :  bpy.props.BoolProperty( default=True )
    def execute(self, context):
        # Get select order list
        context.scene[BONE_SELECTED_ORDER] = []

        def update_selected_bones_order(scene, depsgraph):
            # Check is in Armature modes
            if not context.mode in ['POSE','EDIT_ARMATURE']:
                return {'CANCELLED'}
            
            # get the order list in scene
            orderList = context.scene.get(BONE_SELECTED_ORDER,[])
            # get current selected list
            selected = [bone.name for bone in get_selected_bones(context)]
            # remove bone is already deselected
            orderList = [ bn for bn in orderList if bn in selected ]
            # append new select bone
            for bone in selected[:]:
                if bone not in orderList:
                    orderList.append(bone)

            context.scene[BONE_SELECTED_ORDER] = orderList


        # Trun On
        if self.state:
            bpy.app.handlers.depsgraph_update_post.append(update_selected_bones_order)
            bone_deselect(context)
            self.report({'INFO'}, "Bone Select Order: Trun On")
            
        # Trun Off
        else :     
            if context.scene.get(BONE_SELECTED_ORDER):
                del context.scene[BONE_SELECTED_ORDER]
            handlers = bpy.app.handlers.depsgraph_update_post
            for h in handlers:
                if h.__name__ == 'update_selected_bones_order':
                    handlers.remove(h)  
            self.report({'INFO'}, "Bone Select Order: Trun Off")
        return {'FINISHED'}


# Operator Simple
class F_RENAME_BONE_OT_Copy_To_Others(bpy.types.Operator):
    """Copy active bone's name to others"""
    bl_idname = "format_rename_bone.copy_to_others"
    bl_label = "Copy name"

    def execute(self, context):
        selected_bones = get_selected_bones(context)
        act = get_active_bone(context)
        if not act:
            return {'CANCELLED'}
        newNm = act.name

        newList = []
        counter = 0
        newNm = act.name
        for i,bone in enumerate(selected_bones):
            oldNm = bone.name
            if oldNm != act.name :
                bone.name = f'{newNm}'
                newList.append(bone.name)
                counter+=1
            else :
                newList.append(act.name)
        
        if is_use_order():
            context.scene[BONE_SELECTED_ORDER] = newList
        self.report(type={'INFO'} ,message =f'[Format Rename]: {str(counter)} Bones Renamed')
            
        return {'FINISHED'}
    
class F_RENAME_BONE_OT_Swap_Name(bpy.types.Operator):
    """Swap two bone names"""
    bl_idname = "format_rename_bone.swap_name"
    bl_label = "Switch Name"
    @classmethod
    def poll(cls, context):
        bones = get_selected_bones(context)
        return len(bones)==2
    def execute(self, context):
        bones = get_selected_bones(context)
        boenA = bones[0].name
        boenB = bones[1].name
        bones[0].name = f'{boenA}-Temp_Name_For_Exchange_Names'
        bones[1].name = boenA
        bones[0].name = boenB
        self.report(type={'INFO'} ,message =f'[Format Rename]: {boenA} and {boenB} swapped')
        return {'FINISHED'}
    
# Operator Use Order
class class_use_order():
    @classmethod
    def poll(cls, context):
        return context.scene.get(BONE_SELECTED_ORDER,False)

class F_RENAME_BONE_OT_Order_Set_Team(class_use_order,bpy.types.Operator):
    """Set bones in team A or team B"""
    bl_idname = "format_rename_bone.set_team"
    bl_label = "Set Bone Teams"
    teamID : bpy.props.StringProperty(default='A')
    
    def execute(self, context):
        context.scene[f'bone_team{self.teamID}'] = context.scene.get(BONE_SELECTED_ORDER)
        return {'FINISHED'}


# Others Names Operators
class F_RENAME_BONE_OT_Swap_List_Rotation(class_use_order,bpy.types.Operator):
    """Exchange bone names by List Rotation
['A','B','C'] to ['C','A','B']"""
    bl_idname = "format_rename_bone.swap_list_rotation"
    bl_label = "Switch Name"

    def execute(self, context):
        order_bones = context.scene.get(BONE_SELECTED_ORDER,[])
        obj_bones = get_data_bones(context)
        newList = []
        for i in range(1,len(order_bones)):
            boneA_name = order_bones[i-1]
            boneB_name = order_bones[i]
            boneA = obj_bones.get(boneA_name)
            boneB = obj_bones.get(boneB_name)
            boneA.name = 'Temp_Name_For_Exchange_Names'
            boneB.name = boneA_name
            boneA.name = boneB_name
            newList.append(boneA.name)
        context.scene[BONE_SELECTED_ORDER] = newList
        self.report(type={'INFO'} ,message =f'[Format Rename]: {str(len(newList))} Bones Renamed')
        return {'FINISHED'}

class class_use_teams():
    @classmethod
    def poll(cls, context):
        return context.scene.get(BONE_SELECTED_ORDER,None)

class F_RENAME_BONE_OT_Swap_A_And_B(bpy.types.Operator):
    """Exchange frist and second bone's name
['A','B'] to ['B','A']"""
    bl_idname = "format_rename_bone.swap_a_and_b"
    bl_label = "Switch A & B"
    @classmethod
    def poll(cls, context):
        for team in [BONE_TEAM_A,BONE_TEAM_B]:
            if not context.scene.get(team,False):
                return None
        return True
    def execute(self, context):
        teamA = context.scene.get(BONE_TEAM_A,[])
        teamB = context.scene.get(BONE_TEAM_B,[])
        obj_bones = get_data_bones(context)
        newA =[]
        newB =[]
        for i in range(min(len(teamA),len(teamB))):
            boneA = obj_bones.get(teamA[i],None)
            boneB = obj_bones.get(teamB[i],None)
            if not all([boneA,boneB]):
                continue
            boneA.name = 'Temp_Name_For_Exchange_Names'
            boneB.name = teamA[i]
            boneA.name = teamB[i]
            newA.append(boneA.name)
            newB.append(boneB.name)

        context.scene[BONE_TEAM_A] = newA
        context.scene[BONE_TEAM_B] = newB
        self.report(type={'INFO'} ,message =f'[Format Rename]: Swapped TeamA and TeamB')
        return {'FINISHED'}

class F_RENAME_BONE_OT_Copy_A_To_B(bpy.types.Operator):
    """Copy A team's name to B team"""
    bl_idname = "format_rename_bone.copy_a_to_b"
    bl_label = "Copy A & B"
    @classmethod
    def poll(cls, context):
        return all(context.scene.get(name,None) for name in [BONE_TEAM_A,BONE_TEAM_B])
    def execute(self, context):
        teamA = context.scene.get(BONE_TEAM_A,[])
        teamB = context.scene.get(BONE_TEAM_B,[])
        obj_bones = get_data_bones(context)
        newList =[]
        for i in range(min(len(teamA),len(teamB))):
            bone = obj_bones.get(teamB[i],None)
            if not bone : 
                continue
            bone.name = teamA[i]+'.copyName'
            newList.append(bone.name)
        context.scene[BONE_TEAM_B] = newList
        self.report(type={'INFO'} ,message =f'[Format Rename]: Copied TeamA to TeamB')
        return {'FINISHED'}

# [ Rename ]
class Rename_Operator_Root:
    def word_replace(self,context,bone,fromat_str,order,active_name):
        # order : {a} {A} {Aa} {-Aa} {AA} {-AA} {aa} {-aa} 
        fromat_str = rename_modules.rename_format_to_abc(fromat_str,order)

        # Index : {##}
        fromat_str = rename_modules.rename_format_to_number(fromat_str,order)
        
        # Relationship
        if "{self}" in fromat_str:
            fromat_str = fromat_str.replace("{self}",bone.name)

        if "{parent}" in fromat_str:
            pt = bone.parent
            pt_name = pt.name if pt else ""
            fromat_str = fromat_str.replace("{parent}",pt_name)
        
        if "{active}" in fromat_str:
            fromat_str = fromat_str.replace("{active}",active_name)
        
        if "{shape}" in fromat_str:
            shape_name = bone.custom_shape.name if bone.custom_shape else ''
            fromat_str = fromat_str.replace("{shape}",shape_name)
        
        if "{user}" in fromat_str:
            obj_in_mode = context.object
            if obj_in_mode.type != 'ARMATURE':
                fromat_str = fromat_str.replace("{user}",'')
            fromat_str = fromat_str.replace("{user}",obj_in_mode.data.name)

        if "{scene}" in fromat_str:
            fromat_str = fromat_str.replace("{scene}",context.scene.name)
        if "{view_layer}" in fromat_str:
            fromat_str = fromat_str.replace("{view_layer}",context.view_layer.name)
        # Use Deform : {def,string}
        fromat_str = rename_modules.rename_format_deform(context,fromat_str,bone)
            
        return fromat_str

    def exe_rename(self, context,func_rename):
        fromat_str = getattr(context.scene.format_rename_bone,'rename_str')
        use_order = "update_selected_bones_order" in [f.__name__ for f in bpy.app.handlers.depsgraph_update_post]
        
        # trun in [POSE] Mode
        mode_dict = {'OBJECT':'OBJECT',
                    'EDIT_ARMATURE':'EDIT',
                    'POSE':'POSE'}
        current_mode = context.mode
        bpy.ops.object.mode_set(mode='POSE')

        # Get Bone Names
        if not use_order :
            bones = context.selected_pose_bones
        else :
            order_list = context.scene.get( BONE_SELECTED_ORDER,[] )
            bones = []
            for bone_name in order_list:
                bone = context.object.pose.bones.get(bone_name,False)
                if bone:
                    bones.append(bone)

        if not bones : 
            return {'FINISHED'}
        active_bone = get_active_bone(context).name
        newList = []
        for i,bone in enumerate(bones):
            old_name = bone.name
            replaced_str = self.word_replace(context,bone,fromat_str,i,active_bone)
            func_rename(bone,replaced_str)#f_rename[self.mode](bone,replaced_str)
            print(f'{old_name} is renamed to {bone.name}')
            newList.append(bone.name)
        if use_order:
            context.scene[BONE_SELECTED_ORDER] = newList

        # Back Mode
        bpy.ops.object.mode_set(mode=mode_dict[current_mode])

class F_RENAME_BONE_OT_Rename(Rename_Operator_Root,bpy.types.Operator):
    """Format rename bones"""
    bl_idname = "format_rename_bone.rename"
    bl_label = "Rename"
    
    def execute(self, context):
        func_rename=lambda bone,replaced_str: setattr(bone,'name',replaced_str)
        self.exe_rename(context,func_rename)
        return {'FINISHED'}

class F_RENAME_BONE_OT_Add_Prefix(Rename_Operator_Root,bpy.types.Operator):
    """Add Prefix To Bone Name"""
    bl_idname = "format_rename_bone.add_prefix"
    bl_label = "Add Prefix"
    
    def execute(self, context):
        func_rename=lambda bone,replaced_str: setattr(bone,'name',replaced_str+bone.name)
        self.exe_rename(context,func_rename)
        return {'FINISHED'}

class F_RENAME_BONE_OT_Add_Suffix(Rename_Operator_Root,bpy.types.Operator):
    """Add Suffix To Bone Name"""
    bl_idname = "format_rename_bone.add_suffix"
    bl_label = "Add Suffix"
    mode : bpy.props.StringProperty()
    
    def execute(self, context):
        func_rename=lambda bone,replaced_str: setattr(bone,'name',bone.name+replaced_str)
        self.exe_rename(context,func_rename)
        return {'FINISHED'}

# [ Remove ]
def function_remove_words(self, context,remove_func):
    use_order = "update_selected_bones_order" in [f.__name__ for f in bpy.app.handlers.depsgraph_update_post]
    
    bns = get_selected_bones(context)
    if not bns:
        return {'FINISHED'}
    newList = []
    for bn in bns:
        bn.name = remove_func(bn)
        newList.append(bn.name)

    if use_order:
        context.scene[BONE_SELECTED_ORDER] = newList

class F_RENAME_BONE_OT_Remove_Prefix(bpy.types.Operator):
    """Remove Bone Name Frist Character"""
    bl_idname = "format_rename_bone.remove_prefix"
    bl_label = "Remove Frist Character"
    mode : bpy.props.StringProperty()
    
    def execute(self, context):
        remove_func = lambda x:x.name[1:]
        
        function_remove_words(self, context,remove_func)
        return {'FINISHED'}

class F_RENAME_BONE_OT_Remove_Suffix(bpy.types.Operator):
    """Remove Bone Name Last Character"""
    bl_idname = "format_rename_bone.remove_suffix"
    bl_label = "Remove Bone Last Character"
    mode : bpy.props.StringProperty()
    
    def execute(self, context):
        remove_func = lambda x:x.name[:-1]
        function_remove_words(self, context,remove_func)
        return {'FINISHED'}
  
# [ Rename By Bone-Tree ]

class F_RENAME_BONE_OT_RenameByBoneTree(bpy.types.Operator):
    """Rename Use Relationship Tree
- Vertical Relationship use index (0,1,2...)
- Horizontal Relationship use uppercase (A,B,C...)"""

    bl_idname = "format_rename_bone.rename_by_bone_tree"
    bl_label = "Use Select Order Toggle"

    # BaseName
    use_root_name : bpy.props.BoolProperty( default=True)
    base_name : bpy.props.StringProperty(default='')
    # Branch
    branch_joinsign : bpy.props.StringProperty(default='_')
    # Chain
    chain_joinsign : bpy.props.StringProperty(default='_')
    chain_index_digit : bpy.props.IntProperty(default=1,min=1,max=5)
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self,width=300, title='Rename By Tree', confirm_text='Rename', cancel_default=False, text_ctxt='', translate=True)
        
    def draw(self, context):
        layout = self.layout
        
        col = layout.column()
        col.prop(self,'use_root_name',text='Use Roots Name')
        col = layout.column()
        col.enabled = not self.use_root_name
        col.prop(self,'base_name',text='Base')
        
        col = layout.column()
        col.prop(self,'branch_joinsign',text='Branch Sign')
        col.prop(self,'chain_joinsign',text='Chain Sign')
        col.prop(self,'chain_index_digit',text='Chain Digit')


    def execute(self, context):

        # Get Bones and Roots
        def rename_single_root(rootBone,branch_id,level):
            if self.use_root_name :
                newName = rootBone.name
            else:
                newName = self.base_name
            rootBone.name = newName
            rename_next(rootBone.children,level+1,branch_id,rootBone)
        
        def rename_chain(root_bone,bone,branch_id,level):
            rootName= root_bone.name if self.use_root_name else self.base_name

            level_str = str(level).rjust(self.chain_index_digit,'0')
            if branch_id == '':
                newName = f'{rootName}{self.chain_joinsign}{level_str}'

            else:
                newName = f'{rootName}{self.branch_joinsign}{branch_id}{self.chain_joinsign}{level_str}'
            bone.name = newName
            rename_next(bone.children,level+1,branch_id,root_bone)
        
        def rename_branch_roots( bones_in_selected,root_bone,branch_id ):
            if self.use_root_name:
                for bone in bones_in_selected :
                    rename_next(bone.children,1,'',bone)
            else:
                rename_branch( bones_in_selected,root_bone,branch_id )

        def rename_branch( bones_in_selected,root_bone,branch_id ):
            for kid_index,bone in enumerate(bones_in_selected):
                rootName = root_bone.name if self.use_root_name else self.base_name
                current_id = branch_id+ rename_modules.index_to_Aa(kid_index,is_reverse=False).title()
                newName = f'{rootName}{self.branch_joinsign}{current_id}'
                bone.name = newName
                rename_next(bone.children,1,current_id,root_bone)
        
        def rename_next(bones,level,branch_id,root_bone=None):
            bones_in_selected=[b for b in bones if b in selected_bones]
            selected_bone_num = len(bones_in_selected)
            if not bones_in_selected:
                return None
            
            # Roots
            if level==0:
                if selected_bone_num == 1:
                    rename_single_root(bones_in_selected[0], branch_id, level)
                else:
                    rename_branch_roots( bones_in_selected, root_bone, branch_id )
                return None
            
            # is chain
            if selected_bone_num == 1:
                rename_chain(root_bone, bones_in_selected[0], branch_id, level)
            
            # is Branch
            else :#Abc
                rename_branch(bones_in_selected,root_bone,branch_id)
            return None
        
        selected_bones = get_selected_bones(context)
        
        roots =[b for b in selected_bones if not b.parent in selected_bones ]
        if not roots:
            self.report({'WARNING'}, 'Nothing Selected')
        rename_next(roots,0,'')
        return {'FINISHED'}

# [Format Helper]
class F_RENAME_BONE_OT_Format_Helper(bpy.types.Operator):
    """The penal for format information"""
    bl_idname = "format_rename_bone.format_helper"
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
        row_text(col,'{active}','{active}','Output Active Bone Name','')
        row_text(col,'{shape}','{shape}','Output Bone Shape Name','')
        row_text(col,'{parent}','{parent}','Output Parent Name','')
        row_text(col,'{user}','{user}','Output The Armature Name','')
        row_text(col,'{def}','{def,DEF-}','Output DEF if use deform','')
        row_text(col,'{scene}','{scene}','Output Active Scene Name','')
        row_text(col,'{view_layer}','{view_layer}','Output Active ViewLayer Name','')

# [Replace]
class poll_replace():
    @staticmethod
    def get_bone_list(context,is_use_selected):
        def get_data_bones(context):
            if context.mode == 'POSE': 
                return context.object.data.bones
            if context.mode == 'EDIT_ARMATURE': 
                return context.object.data.edit_bones
            return []
        return context.selected_bones if is_use_selected else get_data_bones(context)

class F_RENAME_BONE_OT_Select_By_Name(poll_replace,bpy.types.Operator):
    """"Select By Object Name"""
    bl_idname = "format_rename_bone.select_by_name"
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
        old_list = self.get_bone_list(context,is_use_selected)
        new_list = rename_modules.re_filter_element(old_list,sreach_txt,pattern_mode)
        
        if new_list=='ERROR':
            self.report(type={'WARNING'} ,message ='[ERROR] Sreach input error')
            return {'FINISHED'}
        
        # Deselect Mode
        deselect_mode = {'EDIT_ARMATURE':bpy.ops.armature.select_all,
                         'POSE':bpy.ops.pose.select_all}
        deselect_mode[context.mode](action='DESELECT')

        # Re-select
        if context.mode == 'POSE':
            pose_bones = context.object.pose.bones
            for bone in new_list:
                if context.blend_data.version[0]<5:
                    bone.select = True
                else:
                    poseBone = pose_bones.get(bone.name,None)
                    poseBone.select = True
            if not context.object.data.bones.active in new_list:
                context.object.data.bones.active = new_list[0]
        if context.mode == 'EDIT_ARMATURE':
            edit_bones = context.object.data.edit_bones
            bones_in_mode = []
            for b in new_list:
                editBone = edit_bones.get(b.name,None)
                editBone.select = True
                editBone.select_head = True
                editBone.select_tail = True
                if editBone:
                    bones_in_mode.append(editBone)
            if not edit_bones.active in bones_in_mode:
                edit_bones.active = bones_in_mode[0]


        return {'FINISHED'}


    
class F_RENAME_BONE_OT_Replace_Name(poll_replace,bpy.types.Operator):
    """"Replace Object Name"""
    bl_idname = "format_rename_bone.replace_name"
    bl_label = "Replace Bones Name"

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
        
        select_list = self.get_bone_list(context,is_use_selected)
        rename_modules.rename_element(self,select_list,sreach_txt,replace_txt,pattern_mode)
        return {'FINISHED'}
        

classes = [ 
            F_RENAME_BONE_OT_Rename,
            F_RENAME_BONE_OT_Add_Prefix,
            F_RENAME_BONE_OT_Add_Suffix,
            F_RENAME_BONE_OT_Remove_Prefix,
            F_RENAME_BONE_OT_Remove_Suffix,
            F_RENAME_BONE_OT_Order_Toggle,
            F_RENAME_BONE_OT_Order_Set_Team,
            F_RENAME_BONE_OT_Swap_Name,
            F_RENAME_BONE_OT_Swap_A_And_B,
            F_RENAME_BONE_OT_Swap_List_Rotation,
            F_RENAME_BONE_OT_Copy_A_To_B,
            F_RENAME_BONE_OT_RenameByBoneTree,
            F_RENAME_BONE_OT_Format_Helper,
            F_RENAME_BONE_OT_Copy_To_Others,
            F_RENAME_BONE_OT_Select_By_Name,
            F_RENAME_BONE_OT_Replace_Name,
            ]

# [ Register ]
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


