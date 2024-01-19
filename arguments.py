import argparse

parser = argparse.ArgumentParser(
    description="Compiler for LazyCMD",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

parser.add_argument("in",
                    type = argparse.FileType("r"),
                    help = "Input file, typically an .lazycmd file",
                    )

parser.add_argument("-c","--comments",
                    choices = ["none", "north", "east", "south", "west", "up", "down"],
                    help = "Include comments as signs",
                    default = "none"
                    )

parser.add_argument("facing",
                    choices = ["north", "east", "south", "west", "up", "down"],
                    default = "north",
                    metavar = "dir",
                    help = "Changes the direction that the command block towers face",
                    )

parser.add_argument("-o", "--out",
                    type = argparse.FileType("w"),
                    help = "Output file, prints commands to terminal if not specified",
                    )

args = parser.parse_args()