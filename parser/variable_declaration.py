from lexer.token_class import TokenClass
from parser.expression import Expression

class VariableDeclaration():
    def __init__(self, i_has_a: TokenClass, varident: TokenClass, value: (None | TokenClass | Expression)):
        self.i_has_a = i_has_a
        self.varident = varident
        self.value = value