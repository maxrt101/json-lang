# Json Lang  
Esoteric programming language. The grammar is represented in JSON.  

## Syntax & Example  
Program structure:
```json
{
  "programName": "Program Name",
  "import": [
    // Files to import
  ],
  "variables": {
    // List of variables
  },
  "code": [
    // Code
  ]
}
```

Example JsonLang program looks like this:
```json
{
  "programName": "Test Program",
  "variables": {
    "test": 123
  },
  "code": [
    {"call": {"name": "print", "args": {"var": "test"}}}
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
 - `env` - REPL environment variables
 - `var` - Runtime variables
 - `locals` - Prints local variable
 - `func` - Prints the list pf functions
 - `list` - Lists programs
 - `load` - Loads a program
 - `run_prog` - Runs a program
 - `run` - Runs a function