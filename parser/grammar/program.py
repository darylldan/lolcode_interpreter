from Interpreter.lolcode_interpreter.lexer.token_class import TokenClass
from Interpreter.lolcode_interpreter.parser.grammar.statement import Statement
from Interpreter.lolcode_interpreter.parser.grammar.variable_list import VariableList

class Program():
    def __init__(self, hai: TokenClass, variableList: VariableList, statementList: list[Statement], kthxbye: TokenClass):
        self.hai = TokenClass
        self.variableList = variableList
        self.statementList = statementList
        kthxbye = kthxbye