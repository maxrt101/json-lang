# parser.py

import json

from .errors import ParseError
from .code import Code

class Parser:

    @staticmethod
    def parse(s: str) -> Code:
        try:
            return Code.from_json(Parser.parse_json(s))
        except Exception as e:
            raise ParseError(str(e))

    @staticmethod
    def parse_json(s: str) -> dict:
        return json.loads(s)
