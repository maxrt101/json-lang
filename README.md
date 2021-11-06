# Json Lang  
Esoteric programming language. The grammar is represented using JSON.  

## Syntax & Example  
Program structure:
```json
{
  "program": "Program Name",
  "import": [
    // Files to import
  ],
  "variables": {
    // List of global variables
  },
  "code": [
    // Code
  ]
}
```

Features supported:
 - Global variables
 - Local variables
 - Function calls
 - Function declaration
 - Conditionals (if)
 - Loops (for)
 - Arithmetic & logic operations (`+`, `-`, `*`, `/`, `==`, `!=`, `<`, `>`, `&&`, `||`)
 - Source file importing

Example JsonLang program:
```json
{
  "program": "Example Program",
  "variables": {
    "test": 123
  },
  "code": [
    {"function": {
      "name": "test",
      "args": ["i"],
      "code": [
        {"if": {
          "condition": {"==": [{"local": "i"}, 123]},
          "then": {
            "call": {"name": "print", "args": {"+": [{"local": "i"}, 1]}}
          },
          "else": {
            "call": {"name": "print", "args": {"-": [{"local": "i"}, 1]}}
          }
        }}
      ]
    }},
    {"call": {"name": "test", "args": [{"var": "test"}]}}
  ]
}
```

## How to run  
 - Clone the repo  
 - Run `main.py`  

The usage of `main.py` is `./main.py [FILENAME]`.  
`FILENAME` is the file to run. Without arguments, it runs the REPL.

The REPL supports the following commands:
 - `quit` - Exits the REPL
 - `help` - Prints help msg
 - `reset` - Resets the runtime (state)
 - `env` - REPL environment variables
 - `var` - Runtime variables
 - `locals` - Prints local variable
 - `func` - Prints the list pf functions
 - `list` - Lists programs
 - `load` - Loads a program
 - `run_prog` - Runs a program
 - `run` - Runs a function