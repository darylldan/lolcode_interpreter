from typing import Any
from lexer import TokenType

class TokenClass:
    def __init__(self, token_type: TokenType, classification: str, lexeme: str, literal: Any, line: int):
        self.token_type = token_type
        self.classification  = classification
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self):
        return f"{self.classification} {self.lexeme} {self.literal if self.literal is not None else ''}"