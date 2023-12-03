from typing import Any
from lexer.token_type import TokenType
from misc.errors import Errors

class TokenClass:
    def __init__(self, token_type: TokenType, classification: str, lexeme: str, literal: Any, line: int, error: Errors = None):
        self.token_type = token_type
        self.classification  = classification
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
        self.error = None

    def __str__(self):
        return f"{self.classification} {self.lexeme} {self.literal if self.literal is not None else ''}"