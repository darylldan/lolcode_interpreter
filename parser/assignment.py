from parser.expression import Expression
from lexer.token_class import TokenClass
from parser.statement import Statement

class AssignmentStatement(Statement):
    def __init__(self, r: TokenClass, destination: TokenClass, source: (TokenClass | Expression | Statement)) -> None:
        super().__init__()
        self.r = r
        self.destination = destination
        self.source = source

class ImplicitITAssignment(Statement):
    def __init__(self, value: (TokenClass | Expression)):
        super().__init__()
        self.val = value