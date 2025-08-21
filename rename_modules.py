import bpy
import re

# [ Format string converter ]

def index_to_Aa(number,is_reverse):
    list_abc = 'abcdefghijklmnopqrstuvwxyz'
    def carry_converter(number):
        # 計算26進位並記錄近List內
        index_list = []
        def abc_carry(number):
            if number:
                index_list.insert(0, number % 26)
                abc_carry(number // 26)
        abc_carry(number)
        return index_list
    
    # 小於26的數使用單字母
    if number < 26:
        return list_abc[number]
    
    # 跳過單字母
    number -= 26
    if number == 0 :
        return 'Aa'
    
    # 計算26進位並記錄近List內
    index_list = carry_converter(number)
    current_id = '' if len(index_list)>1 else 'A' # --> A部分需另外加
    for i in index_list:
        current_id += list_abc[i]
    if is_reverse:
        current_id = current_id[::-1]
    
    return current_id

def rename_format_to_abc(fromat_str,order):
    if "{a}" in fromat_str:
        list_abc = 'abcdefghijklmnopqrstuvwxyz'
        fromat_str = fromat_str.replace("{a}",list_abc[order%26])
    if "{A}" in fromat_str:
        list_ABC = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        fromat_str = fromat_str.replace("{A}",list_ABC[order%26])
    if "{Aa}" in fromat_str:
        fromat_str = fromat_str.replace("{Aa}",index_to_Aa(order,False).title())
    if "{-Aa}" in fromat_str:
        fromat_str = fromat_str.replace("{-Aa}",index_to_Aa(order,True).title())
    if "{aa}" in fromat_str:
        fromat_str = fromat_str.replace("{aa}",index_to_Aa(order,False).lower())
    if "{-aa}" in fromat_str:
        fromat_str = fromat_str.replace("{-aa}",index_to_Aa(order,True).lower())
    if "{AA}" in fromat_str:
        fromat_str = fromat_str.replace("{AA}",index_to_Aa(order,False).upper())
    if "{-AA}" in fromat_str:
        fromat_str = fromat_str.replace("{-AA}",index_to_Aa(order,True).upper())
    return fromat_str

def rename_format_to_number(fromat_str,order):
    # {###}
    role = re.compile('{(#+),?(-?\d*)}')
    match_grps = role.findall(fromat_str)
    if not match_grps :
        return fromat_str
    digits = len(match_grps[0][0])
    start_num = 1 if match_grps[0][1]=='' else int(match_grps[0][1])
    current_index = order+start_num
    num = str(abs(current_index)).rjust(digits,'0')
    if current_index<0:
        num = '-'+num

    return role.sub(num,fromat_str)


def rename_format_deform(context,fromat_str,bone):
    # {def,DEF-}<.*?>
    role = re.compile('{def,?(.*?)}')
    match_grps = role.findall(fromat_str)
    if not match_grps :
        return fromat_str
    try : 
        is_deform = bone.use_deform
    except:
        is_deform = bone.bone.use_deform
    if not is_deform:
        return role.sub('',fromat_str)
    if match_grps[0]=='':
        return role.sub('DEF-',fromat_str)
    return role.sub(match_grps[0],fromat_str)




def search_element_use_re(select_list,sreach_txt):
    role =re.compile(sreach_txt)
    try : 
        new_list = [bn for bn in select_list if re.search(role,bn.name)]
        return len(new_list)
    except:
        return ''

def get_found_element_cost(select_list,sreach_txt,pattern_mode):
    if sreach_txt =='':
        return 'NONE'
    try :
        role =re.compile(sreach_txt,pattern_mode)
        list_cost = len([e for e in select_list if role.search(e.name)])
        return 'NONE' if list_cost==0 else list_cost
    except:
        return 'ERROR'

def re_filter_element(old_list,sreach_txt,pattern_mode):
    try :
        role =re.compile(sreach_txt,pattern_mode)
        return [e for e in old_list if role.search(e.name)]
    except:
        return 'ERROR'

def rename_element(self,select_list,sreach_txt,replace_txt,pattern_mode):
    if not select_list:
        self.report(type={'WARNING'} ,message =f'[Format Rename]: Nothing Found')
    try :
        role =re.compile(sreach_txt,pattern_mode)
        for e in select_list:
            oldName = e.name
            newName = role.sub(replace_txt,e.name)
            e.name = newName
        self.report(type={'INFO'} ,message =f'[Format Rename]: {str(len(select_list))} Renamed')
        
    except:
        self.report(type={'ERROR'} ,message =f'[Format Rename]: Sreach input error')


