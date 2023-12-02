from lexer.token_class import TokenClass
from statement import Statement
from expression import Expression

class FlowControl(Statement):
    pass

# class ElseIfStatement(Statement):
#     def __init__(self, mbbe: TokenClass, expression: Expression) -> None:
#         super().__init__()

class IfElseStatement(FlowControl):
    def __init__(self, o_rly: TokenClass, ya_rly: TokenClass, true_statements: list[Statement], no_wai: TokenClass, false_statements: list[Statement], oic: TokenClass) -> None:
        super().__init__()
        self.o_rly = o_rly
        self.ya_rly = ya_rly
        self.true_statements = true_statements
        self.no_wai = no_wai
        self.false_statements = false_statements
        self.oic = oic

class SwitchCaseCase():
    def __init__(self, omg: TokenClass, statements: list[Statement]) -> None:
        self.omg = omg
        self.statements = statements
        
class SwitchCaseDefault():
    def __init__(self, omgwtf: TokenClass, statements: list[Statement]) -> None:
        self.omgwtf = omgwtf
        self.statements = statements

class SwitchCaseStatement(FlowControl):
    def __init__(self, wtf: TokenClass, cases: list[SwitchCaseCase], default_case: SwitchCaseDefault, oic: TokenClass) -> None:
        super().__init__()
        self.wtf = wtf
        self.cases = cases
        self.default_case = default_case
        self.oic = oic

class LoopCondition():
    def __init__(self, comparison: TokenClass, expression: Expression) -> None:
            self.comparison = comparison
            self.expression = expression

class LoopStatement(FlowControl):
    def __init__(self, im_in_yr: TokenClass, loopident: TokenClass, step: TokenClass, yr: TokenClass, counter: TokenClass, ) -> None:
        super().__init__()
        self.im_in_yr = im_in_yr
        self.loopident = loopident
        self.step = step    # UPPIN or NERFIN
        self.yr = yr
        self.counter = counter