from arguments import *
from classes import *

import preprocessing
import regex as re
import os

LAZYCMD_DIR = os.path.split(__file__)[0]
FILE_DIR = os.path.split(getattr(args, "in").name)[0]

def display_summon_command(name: str, command: str) -> None:
    command_length = len(command)
    
    if command_length > 3500:
        print(f"{name} is too big to fit in a single command block. Split it up in the original file! ({len(command)}/3500 chars)")
    else:
        print(f"\nTower {name}:\n{command}({command_length}/3500 chars)")

def write_summon_command(file, name: str, command: str) -> None:
    command_length = len(command)
    
    if command_length > 3500:
        file.write(f"{name} is too big to fit in a single command block. Split it up in the original file! ({len(command)}/3500 chars)\n")
    else:
        file.write(f"\nTower {name}:\n{command}({command_length}/3500 chars)\n")
   
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

def parse_commands(command_list: list[str]) -> list[Command]:
    commands = []
    
    for line in command_list:
        comment = re.findall(r"//.*", line) # Find comment in line (if any)
        line = re.sub(r"//.*", "", line).rstrip() # Remove comment (if any)
        
        line = line.replace('"', '\\"').replace("'", "\\'") # Escape all quotes
        
        if line[:1].isspace(): # Checks if the line is indented.
            conditional = True
        else:
            conditional = False
        
        line = line.strip()
        
        commands += [Command(line, conditional, comment)]
    
    return commands
    

program_file = getattr(args, "in").read()
output_file = getattr(args, "out")

defined_macros = re.findall(r"macro .*\n-+\n[\s\S]*?\n-+", program_file)
all_macros = preprocessing.find_all_macros(defined_macros, program_file)

included_files = re.findall(r"(?<!\w[ \t]*)include [<'\"]\w+\.\w+[>'\"]\n", program_file)

for filename in included_files:
    filename = filename.split()[1]
    check_char = filename[0]
    filename = filename[1:][:-1] # Trim start and end characters
    
    if check_char == "<":
        file = open(os.path.join(LAZYCMD_DIR, "include", filename))
    elif check_char in ['"', "'"]:
        file = open(os.path.join(FILE_DIR, filename))
    else:
        raise IncorrectIncludeError(f"'include {filename}' formatted incorrectly. Surround file in angle brackets or quotes.")
    
    include_file = file.read()
    file.close()
    
    defined_macros = re.findall(r"macro .*\n-+\n[\s\S]*?\n-+", include_file)
    all_macros += preprocessing.find_all_macros(defined_macros, include_file)

all_towers = re.findall(r"tower .*\n-+\n[\s\S]*?\n-+", program_file)
all_towers = preprocessing.substitute_macros(all_macros, all_towers)
all_towers = preprocessing.split_long_towers(all_towers, getattr(args, "facing"))

for tower in all_towers:
    lines = tower.splitlines()
    
    position = find_relative_position(lines[0])
    tower_name = lines[0][6:] # Removes "tower " from line, leaving tower name and relative position.
    is_continued = tower_name.endswith(" cont")
    tower_name = tower_name.replace(" cont", "")
    
    lines = lines[2:][:-1] # Trim tower name and - lines
    
    commands = parse_commands(lines)
    
    chain = CommandChain(commands, RelativeCoordinate(*position), getattr(args, "facing"), is_continued).to_list()
    chain += ["kill @e[type=command_block_minecart,distance=..2]"]
    
    tower_cart = "summon falling_block ~ ~1 ~ {Time:1,Passengers:[" + str(CommandBlockMinecart(chain)) + ']}\n'
    
    if output_file == None:
        display_summon_command(tower_name, tower_cart)
    else:
        write_summon_command(output_file, tower_name, tower_cart)