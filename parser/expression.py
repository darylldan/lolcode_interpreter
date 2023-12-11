from abc import abstractmethod
from lexer.token_class import TokenClass
from parser.expression_node import ExpressionNode
from parser.statement import Statement

class Expression(Statement):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def eval():
        pass

class BooleanExpression(Expression):
    def __init__(self, head: ExpressionNode = None) -> None:
        super().__init__()
        self.head = head

    def eval():
        'evaluate the expression'

class AnyOfExpression(Expression):
    def __init__(self, any_of: TokenClass, params: list[BooleanExpression | TokenClass] = None) -> None:
        super().__init__()
        self.any_of = any_of
        self.params = []

    def add_param(self, param: (BooleanExpression | TokenClass)):
        self.params.append(param)

    def has_params(self) -> bool:
        return len(self.params) != 0

class AllOfExpression(Expression):
    def __init__(self, all_of: TokenClass, params: list[BooleanExpression | TokenClass] = None) -> None:
        super().__init__()
        self.all_of = all_of
        self.params = []

    def add_param(self, param: (BooleanExpression | TokenClass)):
        self.params.append(param)

    def has_params(self) -> bool:
        return len(self.params) != 0

class ArithmeticExpression(Expression):
    def __init__(self, head: ExpressionNode = None) -> None:
        super().__init__()
        self.head = head

    def eval():
        'evaluate the expression'

class StringConcatenation(Expression):
    def __init__(self, smoosh: TokenClass, args: list[TokenClass]):
        self.smoosh = smoosh
        self.args = args
    
    def eval():
        ''

    def add_args(self, arg: TokenClass):
        self.args.append(arg)

    def has_args(self) -> bool:
        return len(self.args) != 0

class ComparisonExpression(Expression):
    def __init__(self, head: ExpressionNode = None) -> None:
        super().__init__()
        self.head = head

    def eval():
        'evaluate the expression'