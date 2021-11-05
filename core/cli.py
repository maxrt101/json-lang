# cli.py

from .runtime import Runtime
from .errors import UnknownCommandError
from .parser import Parser

import traceback
import readline
import sys

class Repl:
    def __init__(self):
        self.env = {
            'version': '0.1',
            'prompt': '#',
            'color': False,
            'debug': False
        }
        self.rt = Runtime()

    def set_runtime(self, rt):
        self.rt = rt

    def run(self):
        print('JsonLang v' + self.env['version'])
        running = True
        while running:
            try:
                inp = input(self.env['prompt']+' ')
                tokens = list(filter(len, inp.split(' ')))
                if len(tokens) > 0:
                    if tokens[0] == 'quit':
                        running = False
                    elif tokens[0] == 'help':
                        print('JsonLang v' + self.env['version'])
                        print('Interpreter for JsonLang. Type json to execute it')
                        print('Available commands: quit help env var locals func list load run_prog run')
                    elif tokens[0] == 'env':
                        if len(tokens) > 1:
                            if tokens[1] == 'get':
                                if len(tokens) == 3:
                                    print(self.env[tokens[2]])
                                else:
                                    for k, v in self.env.items():
                                        print(f'{k}: {v}')
                            elif tokens[1] == 'set':
                                if len(tokens) >= 4:
                                    self.env[tokens[2]] = ' '.join(tokens[3:])
                                else:
                                    raise ArgumentMismathError('usage: env set KEY VALUE')    
                            else:
                                raise UnknownCommandError('usage: env [get|set KEY [VALUE]]')
                        else:
                            for k, v in self.env.items():
                                print(f'{k}: {v}')
                    elif tokens[0] == 'var':
                        if len(tokens) == 1:
                            for k, v in self.rt.variables.items():
                                print(f'{k}: {v}')
                        elif len(tokens) > 2:
                            if tokens[1] == 'get':
                                print('{}: {}'.format(tokens[2], self.rt.variables[tokens[2]]))
                            elif tokens[1] == 'set':
                                self.rt.variables[tokens[2]] = self.rt.parse_expr(Parser.parse_json(' '.join(tokens[3:])))
                        else:
                            raise ArgumentMismathError('usage: var [get|set KEY [VALUE]]')
                    elif tokens[0] == 'locals':
                        print(self.rt.locals)
                    elif tokens[0] == 'func':
                        for k, v in self.rt.functions.items():
                            print(f'{k}: {v}')
                    elif tokens[0] == 'list':
                        for k, v in self.rt.programs.items():
                            print(f'{k}: {v}')
                    elif tokens[0] == 'load':
                        if len(tokens) == 2:
                            self.rt.add_program(Parser.parse(open(tokens[1]).read()))
                    elif tokens[0] == 'run_prog':
                        if len(tokens) > 1:
                            self.rt.run_program(' '.join(tokens[1:]))
                    elif tokens[0] == 'run':
                        if len(tokens) > 1:
                            self.rt.invoke_function(tokens[1], [self.rt.parse_expr(x) for x in tokens[2:]])
                    else:
                        self.rt.run_stmt(Parser.parse_json(inp))
            except BaseException as ex:
                if ex.__class__ == KeyboardInterrupt:
                    print('\nKeyboardInterrupt')
                    exit(1)
                print(f'ERROR: {ex.__class__.__name__}: {ex}')
                if self.env['debug']:
                    traceback.print_exc()
