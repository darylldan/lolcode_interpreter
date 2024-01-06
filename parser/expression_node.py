from lexer.token_class import TokenClass

'''
If single operand, the operand is in left
'''
class ExpressionNode():
    def __init__(self,
                 parent: 'ExpressionNode' = None,
                 left: 'ExpressionNode' = None,
                 right: 'ExpressionNode' = None,
                 value: TokenClass = None,
                 single_operand=False) -> None:
        self.single_operand = single_operand
        self.parent = parent
        self.left = left
        self.right = right
        self.value = value
