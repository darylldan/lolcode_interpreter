from lexer.token_class import TokenClass
from parser.statement import Statement
from parser.variable_list import VariableList
from parser.function_table import FunctionTable
from parser.functions import FunctionStatement

class Program():
    def __init__(self):
        self.hai: TokenClass = None
        self.variableList: VariableList = None
        self.statementList: list[Statement] = []
        self.kthxbye: TokenClass = None
        self.func_table: FunctionTable = FunctionTable()

    def add_func(self, func: FunctionStatement) -> bool:
        return self.func_table.add_func(func.funcident.lexeme, func)

    def add_statement(self, statement: Statement):
        self.statementList.append(statement)
