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

def find_relative_position(line: str) -> list[int]:
    relative_pos = re.findall(r"{\s*-?\d+,\s*-?\d+,\s*-?\d+}", line) # Finds if there is a relative position argument in tower definition

    if relative_pos != []:
        position = []
        relative_pos = relative_pos[0][1:][:-1].split(',')
        for x in relative_pos:
            position += [int(x)]
    else:
        position = [0, -1, -2]
    
    return position

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

def split_long_towers(tower_list: list[str], facing: str) -> list[list[str]]:
    split_towers = []
    
    for tower in tower_list:
        lines = tower.splitlines()
        
        approximate_command_length = 120 * len(lines) + sum(len(x) for x in lines) + 100 # Massive overestimation of final command length.
        required_splits = 0
        
        tower_name = re.findall(r"\w+", lines[0][6:])[0]
        starting_position = find_relative_position(lines[0])
        lines = lines[2:][:-1] # Trim tower name and - lines
        
        for i in range(len(lines)):
            lines[i] = re.sub(r"//.*", "", lines[i]).rstrip() # Remove comment (if any)
            lines[i] = lines[i].replace('"', '\\"').replace("'", "\\'") # Escape all quotes
        
        if approximate_command_length < 3400: # better safe than sorry amirite hehehehhe
            split_towers += [tower]

        else: 
            split_tower = []
            required_splits = approximate_command_length // 3400
            split_list_length = len(lines) // (required_splits + 1)
            
            for i in range (required_splits):
                split_tower += [lines[:split_list_length]]
                del lines[:split_list_length]
            
            split_tower += [lines]

            for i in range(len(split_tower)):
                split_tower[i].insert(0, f"tower {tower_name}_{i + 1} {{{', '.join(map(str, starting_position))}}}")
                split_tower[i].insert(1, "--")
                split_tower[i].append("--")
                
                match facing:
                    case "north":
                        starting_position[2] -= split_list_length
                    case "south":
                        starting_position[2] += split_list_length
                    case "west":
                        starting_position[0] -= split_list_length
                    case "east":
                        starting_position[0] += split_list_length
                    case "down":
                        starting_position[1] -= split_list_length
                    case "up":
                        starting_position[1] += split_list_length
            
            for x in split_tower:
                split_towers += ['\n'.join(x)]
        
    return split_towers
        
