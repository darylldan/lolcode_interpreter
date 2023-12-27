from lexer.token_class import TokenClass
from parser.variable_declaration import VariableDeclaration

'''
This class stores all the variable declaration from the wazzup-buhbye scope. Could easily be just an array tho but here we are overthinking and over-engineering shit as always.
'''
class VariableList():
    def __init__(self, wazzup: TokenClass, buhbye: TokenClass = None):
        self.wazzup: TokenClass = wazzup
        self.variable_declarations: list[VariableDeclaration] = []
        self.buhbye: TokenClass = buhbye

    def add_variable_declaration(self, vari_dec: VariableDeclaration):
        self.variable_declarations.append(vari_dec)
