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
    def __init__(self, any_of: TokenClass, params: list[BooleanExpression | TokenClass]) -> None:
        super().__init__()
        self.any_of = any_of
        self.params = params

class AllOfExpression(Expression):
    def __init__(self, all_of: TokenClass, params: list[BooleanExpression | TokenClass]) -> None:
        super().__init__()
        self.all_of = all_of
        self.params = params

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

class ComparisonExpression(Expression):
    def __init__(self, head: ExpressionNode = None) -> None:
        super().__init__()
        self.head = head

    def eval():
        'evaluate the expression'