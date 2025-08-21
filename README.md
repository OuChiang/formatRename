# Format Rename
**Format Rename** is an addon that allows batch renaming of objects in a format way.

Its unique features are:
1. Rename using format way
2. Enable selection order and grouping functionality
3. Search and replace using python re module



# Variable in Format
**Numbers**  
`{#}` : 1,2,3,...
`{##}` : 01,02,03,...
`{##,-1}` : -01,00,01,...

**Alphabet**  
`{A}`: A, B, C, ..., Y, Z, A, ...
`{a}`: a, b, c, ..., y, z, a, ...
`{AA}`: A, B, C, ..., Y, Z, AA, AB, AC, ...
`{Aa}`: A, B, C, ..., Y, Z, Aa, Ab, Ac, ...
`{-AA}`: A, B, C, ..., Y, Z, AA, BA, CA, ...
`{-Aa}`: A, B, C, ..., Y, Z, Aa, Ba, Ca, ...

**Context**  
`{self}`: the original name of the item
`{parent}`: the name of the parent object
`{active}`: the name of the currently active item
`{scene}` : the name of current scene
`{view_layer}` : the name of current view layer

**Type (object only)**
`{data}`: refers to the data name of the object. An empty object will return an empty value.  
`{Type}`, `{type}`, `{TYPE}`: refers to the object's type, shown in `title case`, `lowercase`, or `uppercase` format.  
`{pref}`: refers to a custom replacement word based on the object's type.

**Bone Only**
`{user}`: refers to the armature name the bone belongs to.  
`{def}`: refers to whether the bone has `use_deform` enabled. If not enabled, it will return an empty value.



# Enable Selection Order
By default, when obtaining the selection list, items are arranged by their name.  
When selection order is enabled, the tool will record the selection order.  
This allows certain standardized replacement terms to execute in order and also enables grouping.

**Replacement Terms Using Selection Order**  
`{#}`, `{A}`, `{a}`, `{Aa}`, `{AA}`, `{-Aa}`, `{-AA}`

**Enabling Selection Order also Allows Grouping Functionality**
- You can record selections into TeamA and TeamB.
- You can swap names between teams A and B, switching names sequentially.
- You can copy names from TeamA to TeamB in order.



# Search and Replace Functionality

This feature directly uses the Python `re` module, meaning you can use patterns to search for and match objects.

**Select**  
`Selected Only`: When disabled, it searches across the entire scene; when enabled, it filters within the selected items.

**Flags**  
`ASCII Only`: Executes ASCII-only matching with `\w`, `\W`, `\b`, `\B`, `\d`, `\D`, `\s`, `\S`

`Ignore Case`: Executes case-insensitive matching.



**Pattern Example**

`^` : Matches the start of the string

`$` : Matches the end of the string

`[^\x00-\x7F]+` : Matches not ASCII in string

...
