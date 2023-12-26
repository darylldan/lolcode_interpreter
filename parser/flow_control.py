from parser.statement import Statement
from parser.expression import Expression
from lexer.token_class import TokenClass

class FlowControl(Statement):
    pass

# class ElseIfStatement(Statement):
#     def __init__(self, mbbe: TokenClass, expression: Expression) -> None:
#         super().__init__()

class IfElseStatement(FlowControl):
    def __init__(self, o_rly: TokenClass, ya_rly: TokenClass, true_statements: list[Statement] = None, no_wai: TokenClass = None, false_statements: list[Statement] = None, oic: TokenClass = None) -> None:
        super().__init__()
        self.o_rly = o_rly
        self.ya_rly = ya_rly
        self.true_statements = []
        self.no_wai = no_wai
        self.false_statements = []
        self.oic = oic

    def add_true(self, statement: Statement) -> None:
        self.true_statements.append(statement)

    def add_false(self, statement: Statement) -> None:
        self.false_statements.append(statement)

class SwitchCaseCase():
    def __init__(self, omg: TokenClass, key: TokenClass, index: int) -> None:
        self.omg = omg
        self.key = key
        self.index = index
        
class SwitchCaseDefault():
    def __init__(self, omgwtf: TokenClass, index: int) -> None:
        self.omgwtf = omgwtf
        self.index = index
'''
This is a very bad implementation of a switch case, such that it does not have any performance gain
when compared to else-if chain since it stores all the cases in an array, and then iterates through all
the cases until it finds a match on the keys.

A typical switch-case implementation on a most programming languages involves a hashmap for keys with values
being the list of statements to be executed.

Maybe re implement switch case like that in the future?
'''
class SwitchCaseStatement(FlowControl):
    def __init__(self, wtf: TokenClass) -> None:
        super().__init__()
        self.wtf = wtf
        self.cases: list[SwitchCaseCase] = []
        self.statements: list[Statement] = []
        self.default_case: SwitchCaseCase = None
        self.oic = None

    # No need to check if same key exists, will always resolve to first match
    def add_case(self, case: SwitchCaseCase):
        self.cases.append(case)

    def add(self, statement: Statement):
        self.statements.append(statement)

class LoopCondition():
    def __init__(self, comparison: TokenClass = None, expression: (Expression | TokenClass) = None) -> None:
            self.comparison = comparison
            self.expression = expression

class LoopStatement(FlowControl):
    def __init__(self, im_in_yr: TokenClass, loopident: TokenClass = None, step: TokenClass = None, yr: TokenClass = None, counter: TokenClass = None) -> None:
        super().__init__()
        self.im_in_yr = im_in_yr
        self.loopident = loopident
        self.step = step    # UPPIN or NERFIN
        self.yr = yr
        self.counter = counter
        self.statements: list[Statement] = []
        self.loop_cond: LoopCondition = None
        self.im_outta_yr = None
        self.delim_loop_ident = None

    def add(self, statement: (TokenClass | Statement)):
        self.statements.append(statement)

class Terminator(FlowControl):
    def __init__(self, gtfo: TokenClass):
        super().__init__()
        self.gtfo = gtfo