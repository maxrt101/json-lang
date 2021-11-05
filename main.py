#!/usr/bin/env python3

import sys

from core.runtime import Runtime
from core.parser import Parser
from core.cli import Repl

if __name__ == '__main__':
  if len(sys.argv) == 2:
    Runtime.run(Parser.parse(open(sys.argv[1]).read()))
  else:
    Repl().run()

# print(f'Usage: {sys.argv[0]} FILENAME')
