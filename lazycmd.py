from arguments import *
from classes import *

import regex as re

program_file = getattr(args, "in").read()

all_towers = re.findall(r"tower .*\n-+\n[\s\S]*?\n-+", program_file)

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
    
    print(tower_cart if len(tower_cart) <= 3500 else f"is too big to fit in a single command block. ({len(tower_cart)} chars)")