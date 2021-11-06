# runtime.py

from typing import List, Dict, Callable, Any
from functools import reduce
import sys

from .errors import *
from .parser import Parser
from .code import Code

from . import cli

class Constants:
    wildcard_symbol = '_'

class Function:
    def __init__(self, args: List[str], function: Callable[[List], Any]):
        self.args = args
        self.function = function

    def __call__(self, runtime, args: List) -> Any:
        runtime.enter_scope()
        if self.args is None:
            runtime.locals['__args__'] = args
        else:
            if args is None:
                raise ArgumentMismathError(f'Function.__call__(): Expected list, got {type(args)}')
            if len(self.args) == len(args):
                for i in range(len(args)):
                    runtime.locals[self.args[i]] = args[i]
            else:
                raise ArgumentMismathError(f'Expected {len(self.args)} arguments, but got {len(args)}')
        res = runtime.run_block(self.function)
        runtime.exit_scope()
        return res

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
        self.functions = {
            'print': lambda rt, args: print(' '.join(str(x) for x in args))
        }

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
        return self.functions[name](self, args) if name != '' and name in self.functions else None

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
                    return self.variables[name]
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
                    self.__run_block_impl(for_code)
                    self.parse_expr(for_range[2])
                    run = self.parse_expr(for_range[1])
                self.exit_scope()
            else:
                raise JsonLangRuntimeError('"for" expects an object')
        elif cmd == 'while':
            if type(value) == dict:
                self.enter_scope()
                condition, code = None, None
                if 'condition' in value:
                    condition = value['condition']
                if 'code' in value:
                    code = value['code']
                while self.parse_expr(condition):
                    self.__run_block_impl(code)
                self.exit_scope()
            else:
                raise JsonLangRuntimeError('"while" expects an object')
        elif cmd == 'switch':
            if type(value) == dict:
                self.enter_scope()
                switch_value, cases = None, {}
                if 'value' in value:
                    switch_value = str(self.parse_expr(value['value']))
                if 'case' in value:
                    cases = value['case']
                if switch_value in cases:
                    self.__run_block_impl(cases[switch_value])
                elif Constants.wildcard_symbol in cases:
                    self.__run_block_impl(cases[Constants.wildcard_symbol])
                self.exit_scope()
            else:
                raise JsonLangRuntimeError('"while" expects an object')
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
                    self.functions[name] = Function(args, code)
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

    def __run_block_impl(self, code_block) -> Any:
        ret = None
        if type(code_block) == dict:
            for k, v in code_block.items():
                ret = self.parse_stmt(k, v)
        elif type(code_block) == list:
            for s in code_block:
                ret = self.__run_block_impl(s)
        else:
            ret = s

        return ret

    def run_block(self, code_block) -> Any:
        try:
            return self.__run_block_impl(code_block)
        except ReturnException as ex:
            return ex.value

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
