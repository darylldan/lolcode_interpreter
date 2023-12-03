from lexer.token_class import TokenClass
from statement import Statement
from variable_list import VariableList

class Program():
    def __init__(self):
        self.hai: TokenClass = None
        self.variableList: VariableList = None
        self.statementList: list[Statement] = None
        self.kthxbye: TokenClass = None
