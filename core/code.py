# code.py

# program structure
# {
#   "programName": "if_test",
#   "variables": [{"name": "test", "value": True}],
#   "variables": {
#     "test": True
#   }
#   "imports": [
#     "module.json",
#     {"path": "module.json", "relative": True},
#     {"path": "module.json", "objects": "if_test"},
#     {"path": "module.json", "as": "mod"}
#   ],
#   "cmd": [
#     "get": {
#       "args": ["index"],
#       "code": {
#         "return": {"call": {"name": "getValueAt", "args": [{"local": "context"}, {"local": "index"}}
#       }
#     }
#   ],
#   "code": [
#     {"if": {
#       "condition": {"var": "test"},
#       "then": {"call": {"name": "print", "args": "True"}},
#       "else": {"call": {"name": "print", "args": "False"}}
#     }},
#     {"call": {"name": "print", "args": ["Test", {"var": "test"}]}},
#     {"call": "mod.if_test"},
#     {"def": {
#       "name": "printTest",
#       "code": {
#         "call": {"name": "print", "args": {
#             "call": {"name": "split", "args": {"get": 0, "val": {"local": "args"}} }
#           }
#         }
#       }
#     }}
#   ]
# }

#     "class": {
#       "name": "point",
#       "fields": ["x", "y"],
#       "methods": [
#         "add": {"return": {"+": ["x", "y"]}}
#       ]
#     },
#     "set": { "var": "p1", "val": {"new": "point", {"x": 10, "y": 20}} },
#     "call": {"object": "p1", "name": "add"}

# Expression
# {"+": []}

# Command
# {"command": {}}

class Code:
    def __init__(self, name: str, imports: list, variables: list, code: dict):
        self.name = name
        self.imports = imports
        self.variables = variables
        self.code = code
    
    @staticmethod
    def from_json(json):
        program_name = json['program'] if 'program' in json else 'program'
        variables = json['variables'] if 'variables' in json else {}
        imports = json['import'] if 'import' in json else []
        code = json['code'] if 'code' in json else {}
        return Code(program_name, imports, variables, code)
