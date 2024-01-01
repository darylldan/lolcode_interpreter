from lexer.lexer import Lexer
from parser.parser import Parser
from parser.expression import StringConcatenation
from lexer.token_class import TokenClass
from lexer.token_type import TokenType
from semantics.sem_analyzer import SemanticAnalyzer

code = ""

with open("simple.lol", "r") as fp:
    code = fp.read()

x = Lexer(code, silent=True)
y = x.get_lexemes()

# print(str(x) for x in y)

a = Parser(y, code)

if a.successful_parsing:
    b = SemanticAnalyzer(a.main_program, code)

# x = StringConcatenation(TokenClass(TokenType.SMOOSH, "", "", "", 1), [])

# print(isinstance(x, StringConcatenation))