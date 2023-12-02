from expression import Expression
from lexer.token_class import TokenClass
from statement import Statement

class AssignmentStatement(Statement):
    def __init__(self, r: TokenClass, destination: TokenClass, source: (TokenClass | Expression)) -> None:
        super().__init__()
        self.r = r
        self.destination = destination
        self.source = source

class GlobalAssignment(Statement):
    def __init__(self, it: TokenClass, r: TokenClass, expr: Expression):
        self.it = it
        self.r = r
        self.expr = expr