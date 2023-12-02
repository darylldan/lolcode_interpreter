from lexer.token_class import TokenClass
from statement import Statement
from variable_list import VariableList

class Program():
    def __init__(self, hai: TokenClass, variableList: VariableList, statementList: list[Statement], kthxbye: TokenClass):
        self.hai = hai
        self.variableList = variableList
        self.statementList = statementList
        self.kthxbye = kthxbye
