from lexer.token_class import TokenClass
from parser.statement import Statement
from parser.variable_list import VariableList

class Program():
    def __init__(self):
        self.hai: TokenClass = None
        self.variableList: VariableList = None
        self.statementList: list[Statement] = []
        self.kthxbye: TokenClass = None

    def add_statement(self, statement: Statement):
        self.statementList.append(statement)
