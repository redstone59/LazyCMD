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

class RelativeCoordinate:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
    
    def __str__(self):
        return f"~{self.x} ~{self.y} ~{self.z}".replace("~0", "~")

class CommandChain:
    def __init__(self, commands: list, origin = RelativeCoordinate(0, 0, 0), facing = "north"):
        self.commands = commands
        self.origin = origin
        self.facing = facing
        self.increment = 0
    
    def to_list(self):
        resultant = []
        block_coordinate = self.origin
        
        for i in range(len(self.commands)):
            command = f"setblock {block_coordinate} "

            command += "command_block" if i == 0 else "chain_command_block"
            
            block_data = []
            if self.facing != "north": block_data += [f"facing={self.facing}"]
            if self.commands[i].conditional: block_data += ["conditional=true"]
            
            if block_data != []: command += "[" + ",".join(block_data) + "]"
            
            command += "{Command:'"
            command += self.commands[i].command
            command += "'"
            
            if i > 0: command += ",auto:1b"
            
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

class Command:
    def __init__(self, command: str, conditional = False, comment = ""):
        self.command = command
        self.conditional = conditional
        self.comment = comment

class Sign:
    def __init__(self, text: str, facing = "north"):
        self.text = text
        self.facing = facing
    
    def __str__(self):
        return