from lexer.token_class import TokenClass
from parser.statement import Statement
from parser.variable_list import VariableList
from parser.function_table import FunctionTable
from parser.functions import FunctionStatement

'''
Program serves as the Python Object representation of the lolcode program. It contains all the statements formed by bundling the tokens which is done by parser.py


It has also been decided that the function and variables won't share the same namespace.
'''
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
