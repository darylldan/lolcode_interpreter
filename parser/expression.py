from abc import abstractmethod
from tokenize import Token
from lexer.token_class import TokenClass
from parser.statement import Statement

class Expression(Statement):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def eval():
        pass

class BooleanExpression(Expression):
    def __init__(self, expr: list[TokenClass]= None) -> None:
        super().__init__()
        self.expr = []

    def add(self, token: TokenClass):
        self.expr.append(token)

class AnyOfExpression(Expression):
    def __init__(self, head: TokenClass, params: list[BooleanExpression | TokenClass] = None) -> None:
        super().__init__()
        self.head = head
        self.params = []

    def add_param(self, param: (BooleanExpression | TokenClass)):
        self.params.append(param)

    def has_params(self) -> bool:
        return len(self.params) != 0

class AllOfExpression(Expression):
    def __init__(self, head: TokenClass, params: list[BooleanExpression | TokenClass] = None) -> None:
        super().__init__()
        self.head = head
        self.params = []

    def add_param(self, param: (BooleanExpression | TokenClass)):
        self.params.append(param)

    def has_params(self) -> bool:
        return len(self.params) != 0

class ArithmeticExpression(Expression):
    def __init__(self, expr: list[TokenClass] = None) -> None:
        super().__init__()
        self.expr = []

    def add(self, token: TokenClass):
        self.expr.append(token)

class StringConcatenation(Expression):
    def __init__(self, smoosh: TokenClass, args: list[TokenClass] = None):
        self.smoosh = smoosh
        self.args = []
    
    def eval():
        ''

    def add_args(self, arg: TokenClass):
        self.args.append(arg)

    def has_args(self) -> bool:
        return len(self.args) != 0

class ComparisonExpression(Expression):
    def __init__(self, expr: list[TokenClass] = None) -> None:
        super().__init__()
        self.expr = []

    def add(self, token: TokenClass):
        self.expr.append(token)