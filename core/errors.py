# errors.py

class ParseError(Exception):
    def __init__(self, message):
        super().__init__(message)

class JsonLangRuntimeError(Exception):
    def __init__(self, message):
        super().__init__(message)

class ArgumentMismathError(Exception):
    def __init__(self, message):
        super().__init__(message)

class InvalidArgumentsError(Exception):
    def __init__(self, message):
        super().__init__(message)

class UnknownCommandError(Exception):
    def __init__(self, message):
        super().__init__(message)