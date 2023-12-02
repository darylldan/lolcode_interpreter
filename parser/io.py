from ast import Expression
from lexer.token_class import TokenClass
from statement import Statement

class InputStatement(Statement):
    def __init__(self, gimmeh: TokenClass, varident: TokenClass) -> None:
        super().__init__()
        self.gimmeh = gimmeh
        self.varident = varident

class PrintStatement(Statement):
    def __init__(self, visible: TokenClass, args: list[(TokenClass | Expression)]) -> None:
        super().__init__()
        self.visible = visible
        self.args = args
