from statement import Statement
from lexer.token_class import TokenClass

class TypecastStatement(Statement):
    def __init__(self, maek: TokenClass, varident: TokenClass, type: TokenClass):
        self.maek = maek
        self.varident = varident
        self.type = type

class RecastStatement(Statement):
    def __init__(self, varident: TokenClass, is_now_a: TokenClass, type: TokenClass):
        self.is_now_a = is_now_a
        self.varident = varident
        self.type = type