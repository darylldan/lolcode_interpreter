from typing import Any
from lexer.token_type import TokenType

class Symbol():
    def __init__(self, value: Any, type: TokenType):
        self.value = value
        self.type = type
