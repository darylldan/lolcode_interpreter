from lexer.token_class import TokenClass

class ExpressionNode():
    def __init__(self,
                 parent: 'ExpressionNode' = None,
                 operand1: 'ExpressionNode' = None,
                 operand2: 'ExpressionNode' = None,
                 operator: TokenClass = None,
                 value: TokenClass= None, 
                 single_operand=False) -> None:
        self.single_operand = single_operand
        self.parent = parent
        self.operand1 = operand1
        self.operand2 = operand2
        self.operator = operator
        self.value = value
