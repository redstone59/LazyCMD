# LazyCMD - a slightly faster way to make command block towers
LazyCMD was a tool developed in order to make creating command block towers less tedious than it normally is. It has a very simple grammar, meaning there is little to no learning curve at all.

It currently compiles to `summon` commands with command block minecart towers. This means that there is no need to install mods such as WorldEdit to import a schematic, or to use Stucture Blocks. Schematic support may be added in a future update.

This may become the intermediate language for [mCmd](https://github.com/redstone59/mCmd), another project which aims to create a higher-level programming language that can compile into command blocks.

# Prerequisites

Before running LazyCMD, install the `regex` module by running `pip install regex`. This is a different module than Python's included `re` module.

When including other files, be sure to run the `[name]_first_run` macro at least once per world. Another thing that is required is a dummy scoreboard named `constants`. This scoreboard is absolutely necessary for any mathematical operations that are not assignment, addition, or subtraction.

```
include <random.lazyh>                     // Included file

tower setup
--
scoreboard objectives add constants dummy  // Create the constants scoreboard
random_first_run                           // Initalise random.lazyh for the world
--
```

# Grammar

## Towers

A command block tower has two parts, the definition and the contents. 

The definition is started by writing `tower `, followed by the name of the tower (restricted to uppercase and lowercase letters, numbers, and underscores).

A relative position can also be specified to change where the command block tower is placed relative to the command block that will run the outputted `summon` command. If a relative position is not specified, it defaults to `{0, -1, 2}` (two blocks north)

```
tower [tower_name]
tower [tower_name] {relative_x, relative_y, relative_z}
```

The contents of a `tower` is a list of commands, seperated by newlines, with each line being it's own command block. Line comments can be added by preceding the comment with `//`, akin to how C does line comments. Multi-line comments do not exist in LazyCMD, but this will probably change.

```
scoreboard players operation number arguments %= 2 constants // Takes the remainder when dividing the number by 2
execute if score number matches 0 run say The number is even
execute if score number matches 1 run say The number is odd.
```

An indented line in the contents of a tower makes the command block conditional. This is useful when working with more complex `execute if` or `execute unless` statements.

```
execute if entity @a[distance=..5]
    title @a[distance=..5] actionbar "Get off my damn lawn!"
    effect give @a[distance=..5] levitation 5 100 true
```

The contents of a tower **must** be surrounded by two lines comprising of at least one `-` character. Typically `--` is used.

A complete tower would look something like this.
```
tower useless_tower {0, -1, 2} // Definition
--
command 1                      // Impulse command block, needs redstone
command 2                      // Chain command block, always active
    command 3                  // Chain command block, always active, conditional
...
--
```

If the definition of a tower ends with ` cont`, however, the first command block will not be an impulse command block, and instead a chain command block. This is useful if the tower to be placed is being added onto an existing tower.

## Macros

Macros work like `#define` in C, where all instances of the macro are replaced by the contents of the macro, with the arguments provided substituted into the contents. Arguments are not required, however.

A macro is structured the same way as a tower, but with `macro ` instead of `tower `, and the arguments surrounded by parenthesis and seperated by commas. 

Argument names **can not** be the name of a command, e.g. having an argument named `scoreboard` would raise `IncompleteMacroError` when trying to compile. This is to prevent unexpected errors.

A complete macro would look something like this.
```
macro useless_macro (arg_1, arg_2, arg_3) // Definition with arguments
--
say arg_1
say arg_2
    say arg_3                             // Conditional line
--
```

Calling a macro without all arguments specified raises `IncompleteMacroError` when trying to compile.

Using a macro in a tower works the same as calling a function in any programming language. Below is an example using the `useless_macro` defined above.

```
tower useless_tower
--
tp @e @r
useless_macro(a random player, has just gotten, gamer'd)
--
```

When compiling, the macro gets substituted and the tower becomes

```
tower useless_tower
--
tp @e @r
say a random player
say has just gotten
    say gamer'd
--
```

## Including other files

Much like other coding languages, the code in other files can be used if the file is included. In LazyCMD, including another file means that all the macros defined within that file can be used. Towers do not get imported.

The syntax for including files is similar to C. To include a file from the LazyCMD standard library (located in the `include` folder in the same directory that contains `lazycmd.py`), the filename must be surrounded in angle brackets.

```
include <lorem.lazyh> // Imports macros from [lazycmd dir]/include/random.lazyh
```

To include a file in the same directory as the file to be compiled, the filename is surrounded by quotes (single or double)

```
include "ipsum.lazyh" // Imports macros from ./ipsum.lazyh
```

# Compiling

Compiling a `.lazycmd` file is done on the terminal, and is done by the `lazycmd.py` file. The arguments for the compiler are as follows:

`lazycmd.py [-c] in dir [-o output_file] `

* `in` - The input file, typically a `.lazycmd` file
* `dir` - Changes the direction the command block towers face (can be `north`, `south`, `east`, `west`, `up`, `down`)
* `-c` or `--comments` - Include the line comments as signs. Defaults to `none`, or can have a direction (same as `dir`) (*This is currently not implemented*)
* `-o` or `--out` - The output text file to be written to. If not specified, the compiled commands will be outputted to the terminal.