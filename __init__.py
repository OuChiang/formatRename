import bpy
from . import properties
from . import operator_object
from . import operator_bone
from . import presets
from . import panels




class_list=[
    properties,
    presets,
    operator_object,
    operator_bone,
    panels
]

def register():
    for cls in class_list:
        cls.register()

def unregister():
    class_list.reverse()
    for cls in class_list:
        cls.unregister()
    
    