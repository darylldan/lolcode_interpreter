from Interpreter.lolcode_interpreter.lexer.token_class import TokenClass
from Interpreter.lolcode_interpreter.parser.grammar.variable_declaration import VariableDeclaration

class VariableList():
    def __init__(self, wazzup: TokenClass, buhbye: TokenClass):
        self.wazzup: TokenClass = wazzup
        self.variable_declarations: list[VariableDeclaration] = []
        self.buhbye: TokenClass = buhbye

