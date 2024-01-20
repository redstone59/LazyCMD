import regex as re

COMMANDS = [
      "advancement",     "attribute",    "bossbar",
            "clone",          "data",   "datapack",
  "defaultgamemode",    "difficulty",     "effect",
          "enchant",       "execute", "experience",
             "fill",      "function",   "gamemode",
         "gamerule",          "give",       "help",
             "kick",          "kill",       "list",
           "locate",      "particle",     "reload",
              "say",    "scoreboard",       "seed",
         "setblock", "setworldspawn", "spawnpoint",
    "spreadplayers",     "stopsound",     "summon",
              "tag",          "team",    "teammsg",
         "teleport",          "tell",    "tellraw",
             "time",         "title",         "tp",
          "trigger",             "w",    "weather",
      "worldborder",            "xp"
]

class IncompleteMacroError(Exception):
    pass

class IncorrectIncludeError(Exception):
    pass

class RelativeCoordinate:
    def __init__(self, x: int | float, y: int | float, z: int | float):
        self.x = x
        self.y = y
        self.z = z
    
    def __str__(self):
        return f"~{self.x} ~{self.y} ~{self.z}".replace("~0", "~")
    
class CommandBlockMinecart:
    def __init__(self, command: str, passenger = None):        
        if type(command) == list:
            self.command = command[0]
            if len(command[1:]) > 0:
                self.passenger = CommandBlockMinecart(command[1:])
            else:
                self.passenger = None
        else:
            self.command = command
            self.passenger = passenger
        
    def __str__(self):
        resultant = '{id:"command_block_minecart",Command:"'
        resultant += self.command
        resultant += '"'
        if self.passenger != None:
            resultant += f',Passengers:[{self.passenger}]'
        resultant += '}'
        return resultant

class Command:
    def __init__(self, command: str, conditional = False, comment = ""):
        self.command = command
        self.conditional = conditional
        self.comment = comment

class CommandChain:
    def __init__(self, commands: list[Command], origin = RelativeCoordinate(0, 0, 0), facing = "north", continued = False):
        self.commands = commands
        self.origin = origin
        self.facing = facing
        self.increment = 0
        self.continued = continued
    
    def to_list(self):
        resultant = []
        block_coordinate = self.origin
        
        for i in range(len(self.commands)):
            command = f"setblock {block_coordinate} "

            command += "command_block" if i == 0 and not self.continued else "chain_command_block"
            
            block_data = []
            if self.facing != "north": block_data += [f"facing={self.facing}"]
            if self.commands[i].conditional: block_data += ["conditional=true"]
            
            if block_data != []: command += "[" + ",".join(block_data) + "]"
            
            command += "{Command:'"
            command += self.commands[i].command
            command += "'"
            
            if i > 0 or self.continued: command += ",auto:1b"
            
            command += "}"
            
            resultant += [command]

            match self.facing:
                case "north":
                    block_coordinate.z -= 1
                case "south":
                    block_coordinate.z += 1
                case "west":
                    block_coordinate.x -= 1
                case "east":
                    block_coordinate.x += 1
                case "down":
                    block_coordinate.y -= 1
                case "up":
                    block_coordinate.y += 1
                
        return resultant

class Macro:
    def __init__(self, name: str, argument_names: list | None, contents: str):
        if argument_names != None:
            for argument in argument_names:
                if argument in COMMANDS:
                    raise IncompleteMacroError(f"Macro '{name}' contains argument name '{argument}', which is a command. Change to avoid unexpected errors.")
        
        self.name = name
        self.argument_names = argument_names
        self.contents = contents
    
    def line_is_macro(self, line: str):
        return line.strip().startswith(self.name)
    
    def substitute(self, line: str):
        if not self.line_is_macro(line):
            return line
        
        if self.argument_names != None:
            arguments = re.findall(r"\(.*\)", line)
            arguments = re.findall(r"(?<=[\(,])[^\s]*?[^,]+(?=[,\)])", arguments[0])
            
            for i in range(len(arguments)):
                arguments[i] = arguments[i].strip()
            
            if len(arguments) != len(self.argument_names): 
                raise IncompleteMacroError(f"Missing argument for macro {self.name} ({len(arguments)} args instead of {len(self.argument_names)})")
            
            substitute_dict = dict(zip(self.argument_names, arguments))
            
            new_line = "\n".join(self.contents)
            
            for key in substitute_dict:
                substitute = substitute_dict[key].replace('(', '')
                new_line = re.sub(rf"(?<!\w)(?<=[^@]){key}(?!\w)", substitute, new_line)
            
            return new_line.splitlines()

        return self.contents

class Sign:
    def __init__(self, text: str, facing = "north"):
        self.text = text
        self.facing = facing
    
    def __str__(self):
        return