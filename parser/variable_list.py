from lexer.token_class import TokenClass
from variable_declaration import VariableDeclaration

class VariableList():
    def __init__(self, wazzup: TokenClass, buhbye: TokenClass):
        self.wazzup: TokenClass = wazzup
        self.variable_declarations: list[VariableDeclaration] = []
        self.buhbye: TokenClass = buhbye

