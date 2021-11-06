# runtime.py

from typing import List, Dict, Callable, Any
from functools import reduce
import sys

from .errors import *
from .parser import Parser
from .code import Code

from . import cli

class ReturnException(Exception):
    def __init__(self, val):
        super().__init__('return')
        self.value = val

class Runtime:
    def __init__(self):
        self.programs = {}
        self.variables = {}
        self.locals = {}
        self.depth = 0
        self.function_args = {}
        self.functions = {
            'print': lambda args: print(' '.join(str(x) for x in args))
        }

    def wrap_function(self, code: List) -> Callable[[List], Any]:
        return lambda args: self.run_block(code)

    def get_local(self, name: str) -> Any:
        current_locals = self.locals
        while '__parent_locals__' in current_locals:
            if name in current_locals:
                return current_locals[name]
            current_locals = current_locals['__parent_locals__']

    def set_local(self, name: str, value: Any):
        current_locals = self.locals
        while '__parent_locals__' in current_locals:
            if name in current_locals:
                current_locals[name] = value
                break
            current_locals = current_locals['__parent_locals__']

    def add_program(self, code: Code):
        self.programs[code.name] = code

    def invoke_function(self, name: str, args: List):
        if name == '':
            return 
        self.enter_scope()
        if name in self.function_args:
            if args is None:
                raise ArgumentMismathError(f'invoke_function(): Expected list, got {type(args)}') 
            if len(self.function_args[name]) == len(args):
                for i in range(len(args)):
                    self.locals[self.function_args[name][i]] = args[i]
            else:
                raise ArgumentMismathError(f'Function {name} expected {len(self.function_args[name])} arguments, but got {len(args)}')
        else:
            self.locals['__args__'] = args
        res = self.functions[name](args)
        self.exit_scope()        
        return res

    def enter_scope(self):
        self.depth += 1
        new_locals = {'__parent_locals__': self.locals}
        self.locals = new_locals

    def exit_scope(self):
        self.depth -= 1
        self.locals = self.locals['__parent_locals__']

    def parse_expr(self, stmt: Any) -> Any:
        if type(stmt) == dict:
            res = []
            for k, v in stmt.items():
                res.append(self.parse_stmt(k, v))
            if len(res) == 1:
                return res[0]
            return res
        elif type(stmt) == list:
            return [self.parse_expr(x) for x in stmt]
        else:
            return stmt

    def parse_stmt(self, cmd: str, value: Any) -> Any:
        if cmd in ['comment', 'ignore']:
            pass
        elif cmd in ['python', 'py']:
            return eval(value)
        elif cmd == 'print':
            print(self.parse_expr(value))
        elif cmd == 'var':
            if type(value) == str:
                return self.variables[value]
            elif type(value) == dict:
                if 'name' in value:
                    return self.variables[value['name']]
            raise JsonLangRuntimeError('"var" expects an object or a string')
        elif cmd == 'local':
            if type(value) == str:
                return self.get_local(value)
            elif type(value) == dict:
                if 'name' in value and 'value' in value:
                    self.set_local(value['name'], self.parse_expr(value['value']))
                    return self.get_local(value['name'])
            raise JsonLangRuntimeError('"local" expects an object or a string')
        elif cmd == 'set':
            if type(value) == dict:
                name, val = '', ''
                if 'name' in value:
                    name = value['name']
                if 'value' in value:
                    val = value['value']
                if name != '' and val != '':
                    self.variables[name] = self.parse_expr(val)
            else:
                raise JsonLangRuntimeError('"set" expects an object')
        elif cmd == 'set_local':
            if type(value) == dict:
                name, val = '', ''
                if 'name' in value:
                    name = value['name']
                if 'value' in value:
                    val = value['value']
                if name != '' and val != '':
                    self.locals[name] = self.parse_expr(val)
                else:
                    raise InvalidArgumentsError('"set_local" expected name & value')
            else:
                raise JsonLangRuntimeError('"set_local" expects an object')
        elif cmd == 'if':
            if type(value) == dict:
                self.enter_scope()
                cond, then, else_, ret = '', {}, {}, None
                if 'condition' in value:
                    cond = value['condition']
                if 'then' in value:
                    then = value['then']
                if 'else' in value:
                    else_ = value['else']
                if self.parse_expr(cond):
                    ret = self.parse_expr(then)
                else:
                    ret = self.parse_expr(else_)
                self.exit_scope()
                return ret
            raise JsonLangRuntimeError('"if" expects an object')
        elif cmd == 'for':
            if type(value) == dict:
                self.enter_scope()
                for_range, for_code = None, None
                if 'range' in value:
                    for_range = value['range']
                if 'code' in value:
                    for_code = value['code']
                if type(for_range) == list:
                    self.parse_expr(for_range[0])
                # elif type(for_range) == dict: # TODO: range-based for loops
                run = self.parse_expr(for_range[1])
                while run:
                    self.run_block(for_code)
                    self.parse_expr(for_range[2])
                    run = self.parse_expr(for_range[1])
                self.exit_scope()
            else:
                raise JsonLangRuntimeError('"for" expects an object')
        elif cmd == 'while':
            pass
        elif cmd == 'switch':
            pass
        elif cmd in ['def', 'function']:
            if type(value) == dict:
                name, code, args = '', {}, []
                if 'name' in value:
                    name = value['name']
                if 'args' in value:
                    args = value['args']
                if 'code' in value:
                    code = value['code']
                if name != '':
                    self.functions[name] = self.wrap_function(code)
                    self.function_args[name] = args
            else:
                raise JsonLangRuntimeError('"def" expects an object')
        elif cmd == 'call':
            name, args = '', []
            if type(value) == str:
                name = value
            elif type(value) == dict:
                if 'name' in value:
                    name = value['name']
                if 'args' in value:
                    if type(value['args']) == list:
                        args = [self.parse_expr(x) for x in value['args']]
                    else:
                        args.append(self.parse_expr(value['args']))
            else:
                raise JsonLangRuntimeError('"call" expects an object or a string')
            return self.invoke_function(name, args)
        elif cmd == 'return':
            raise ReturnException(value)
        elif cmd == 'import':
            if type(value) == list:
                for x in value:
                    self.import_program(x)
            elif type(value) == str:
                self.import_program(value)
            else:
                raise JsonLangRuntimeError('"import" expects a list or a string') 
        elif cmd == 'breakpoint': # TODO: breakpoints
            if value == 'cli':
                repl = cli.Repl()
                repl.set_runtime(self)
                repl.run()
        elif cmd in ['+', 'add']:
            if type(value) == list:
                return reduce(lambda x, y: x + y, [self.parse_expr(x) for x in value])
            raise JsonLangRuntimeError('"+" expects a list') 
        elif cmd in ['-', 'sub']:
            if type(value) == list:
                return reduce(lambda x, y: x - y, [self.parse_expr(x) for x in value])
            raise JsonLangRuntimeError('"-" expects a list')
        elif cmd in ['*', 'mul']:
            if type(value) == list:
                return reduce(lambda x, y: x * y, [self.parse_expr(x) for x in value])
            raise JsonLangRuntimeError('"*" expects a list')
        elif cmd in ['/', 'div']:
            if type(value) == list:
                return reduce(lambda x, y: x / y, [self.parse_expr(x) for x in value])
            raise JsonLangRuntimeError('"/" expects a list')
        elif cmd in ['==', 'eq']:
            if type(value) == list:
                return reduce(lambda x, y: x == y, [self.parse_expr(x) for x in value])
            raise JsonLangRuntimeError('"==" expects a list')
        elif cmd in ['!=', 'ne']:
            if type(value) == list:
                return reduce(lambda x, y: x != y, [self.parse_expr(x) for x in value])
            raise JsonLangRuntimeError('"!=" expects a list')
        elif cmd in ['<', 'lt']:
            if type(value) == list:
                return reduce(lambda x, y: x < y, [self.parse_expr(x) for x in value])
            raise JsonLangRuntimeError('"<" expects a list')
        elif cmd in ['>', 'gt']:
            if type(value) == list:
                return reduce(lambda x, y: x > y, [self.parse_expr(x) for x in value])
            raise JsonLangRuntimeError('">" expects a list')
        elif cmd in ['&&', 'and']:
            if type(value) == list:
                return reduce(lambda x, y: x and y, [self.parse_expr(x) for x in value])
            raise JsonLangRuntimeError('"&&" expects a list')
        elif cmd in ['||', 'or']:
            if type(value) == list:
                return reduce(lambda x, y: x or y, [self.parse_expr(x) for x in value])
            raise JsonLangRuntimeError('"||" expects a list')
        else:
            raise UnknownCommandError(f'Unrecognized command "{cmd}"')

    def run_stmt(self, code: Dict):
        for k, v in code.items():
            self.parse_stmt(k, v)

    def run_block(self, code_block: List) -> Any:
        ret = None
        try:
            for s in code_block:
                if type(s) == dict:
                    for k, v in s.items():
                        ret = self.parse_stmt(k, v)
                elif type(s) == list:
                    ret = self.run_block(s)
                else:
                    ret = s
        except ReturnException as ex:
            ret = ex.value
        return ret

    def run_code(self, code: Code):
        self.variables.update(code.variables)
        for x in code.imports:
            self.import_program(x)
        self.run_block(code.code)

    def run_program(self, name: str):
        self.run_code(self.programs[name])

    def import_program(self, file_name: str):
        code = Code.from_json(Parser.parse_json(open(file_name).read()))
        self.add_program(code)
        self.run_program(code.name)

    @staticmethod
    def run(code: Code):
        rt = Runtime()
        rt.add_program(code)
        rt.run_program(code.name)
