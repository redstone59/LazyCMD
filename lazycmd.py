from arguments import *
from classes import *

import regex as re

program_file = getattr(args, "in").read()

defined_macros = re.findall(r"macro .*\n-+\n[\s\S]*?\n-+", program_file)
all_macros = []

for macro in defined_macros:
    program_file.replace(macro, "")
    lines = macro.splitlines()
    definition = lines[0][6:]

    macro_arguments = re.findall(r"\(.*\)", definition)
    if macro_arguments != []:
        macro_arguments = re.findall(r"\w+(?=[,\)])", macro_arguments[0])
    else:
        macro_arguments = None
    
    macro_name = re.findall(r"\w+", definition)[0]
    
    all_macros += [Macro(macro_name, macro_arguments, lines[2:][:-1])]

all_towers = re.findall(r"tower .*\n-+\n[\s\S]*?\n-+", program_file)
substituted_lines = {}

for macro in all_macros:
    for i in range(len(all_towers)):
        tower = all_towers[i]
        lines = tower.splitlines()

        for j in range (len(lines)):
            macro_line = lines[j]
            lines[j] = re.sub(r"//.*", "", lines[j]).rstrip() # Remove comment (if any)
            
            if macro.line_is_macro(lines[j]):
                print(lines[j])
                substituted_lines[j] = macro.substitute(lines[j])

        substituted_lines = dict(sorted(substituted_lines.items(), reverse = True))

        for j in substituted_lines:
            del lines[j]
            lines[j:j] = substituted_lines[j]

        all_towers[i] = "\n".join(lines)


for tower in all_towers:
    lines = tower.splitlines()
    relative_pos = re.findall(r"{\s*-?\d+,\s*-?\d+,\s*-?\d+}", lines[0]) # Finds if there is a relative position argument in tower definition
    
    if relative_pos != []:
        position = []
        relative_pos = relative_pos[0][1:][:-1].split(',')
        for x in relative_pos:
            position += [int(x)]
    else:
        position = [0, -1, -2]
    
    print(f"Tower {lines[0][6:]}:")
    
    lines = lines[2:][:-1] # Remove tower name and - lines
    commands = []
    
    for line in lines:
        comment = re.findall(r"//.*", line) # Find comment in line (if any)
        line = re.sub(r"//.*", "", line).rstrip() # Remove comment (if any)
        
        for macro in all_macros:
            if macro.line_is_macro(line):
                line = macro.substitute(line)
        
        line = line.replace('"', '\\"').replace("'", "\\'") # Escape all quotes
        
        if line[:1].isspace(): # Checks if the line is indented.
            conditional = True
        else:
            conditional = False
        
        line = line.strip()
        
        commands += [Command(line, conditional, comment)]
    
    chain = CommandChain(commands, RelativeCoordinate(*position), getattr(args, "facing")).to_list()
    chain += ["kill @e[type=command_block_minecart,distance=..2]"]
    tower_cart = "summon falling_block ~ ~1 ~ {Time:1,Passengers:[" + str(CommandBlockMinecart(chain)) + ']}\n'
    
    print(tower_cart if len(tower_cart) <= 3500 else f"is too big to fit in a single command block. Split it up in the original file! ({len(tower_cart)} chars)")
    print(len(tower_cart))