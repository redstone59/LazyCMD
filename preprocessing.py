from classes import *
import regex as re

def find_all_macros(macro_definitions: list[str], file_contents: str) -> list[Macro]:
    all_macros = []
    
    for macro in macro_definitions:
        file_contents.replace(macro, "")
        lines = macro.splitlines()
        definition = lines[0][6:]

        macro_arguments = re.findall(r"\(.*\)", definition)
        if macro_arguments != []:
            macro_arguments = re.findall(r"\w+(?=[,\)])", macro_arguments[0])
        else:
            macro_arguments = None
        
        macro_name = re.findall(r"\w+", definition)[0]
        
        all_macros += [Macro(macro_name, macro_arguments, lines[2:][:-1])]
    
    return all_macros

def substitute_macros(macro_list: list[Macro], tower_list: list[str]) -> str:
    for macro in macro_list:
        for i in range(len(tower_list)):
            lines = tower_list[i].splitlines()
            substituted_lines = {}

            for j in range (len(lines)):
                macro_line = lines[j]
                lines[j] = re.sub(r"//.*", "", lines[j]).rstrip() # Remove comment (if any)
                
                if macro.line_is_macro(lines[j]):
                    substituted_lines[j] = macro.substitute(lines[j])

            substituted_lines = dict(sorted(substituted_lines.items(), reverse = True))

            for j in substituted_lines:
                del lines[j]
                lines[j:j] = substituted_lines[j]

            tower_list[i] = "\n".join(lines)
    
    return tower_list
"""
def split_long_towers():
    split_towers = []
    for tower in all_towers:
        lines = tower.splitlines()
        for i in range(len(lines)):
            lines[i] = re.sub(r"//.*", "", lines[i]).rstrip() # Remove comment (if any)
            lines[i] = lines[i].replace('"', '\\"').replace("'", "\\'") # Escape all quotes
        
        approximate_command_length = 120 * len(lines) + sum(len(x) for x in lines) + 100 # Massive overestimation of final command length.
        required_splits = 0
        
        if approximate_command_length >= 3400: # better safe than sorry amirite hehehehhe
            required_splits = approximate_command_length // 3400
            split_list_length = len(lines) // (required_splits + 1)
            for i in range (required_splits + 1):
                print(lines[:split_list_length])
                del lines[:split_list_length]
            print(lines[:split_list_length])
        
        
        print((len(lines), required_splits, split_list_length))
"""