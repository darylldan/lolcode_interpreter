from lexer.token_class import TokenClass
from parser.variable_declaration import VariableDeclaration

class VariableList():
    def __init__(self, wazzup: TokenClass, buhbye: TokenClass = None):
        self.wazzup: TokenClass = wazzup
        self.variable_declarations: list[VariableDeclaration] = []
        self.buhbye: TokenClass = buhbye

    def add_variable_declaration(self, vari_dec: VariableDeclaration):
        self.variable_declarations.append(vari_dec)
