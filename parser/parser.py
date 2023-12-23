from lexer.token_class import TokenClass
from lexer.token_type import TokenType
from misc.errors import Errors
from parser.program import Program
from parser.variable_list import VariableList
from parser.variable_declaration import VariableDeclaration
from parser.io import InputStatement, PrintStatement
from parser.expression import *
from parser.assignment import AssignmentStatement
from parser.typecast import TypecastStatement, RecastStatement
from parser.flow_control import IfElseStatement, SwitchCaseStatement, SwitchCaseCase, SwitchCaseDefault, LoopStatement, LoopCondition 
from parser.functions import FunctionStatement, FunctionCallStatement, FunctionReturn
import sys  

def prRed(skk): print("\033[91m {}\033[00m" .format(skk), file=sys.stderr, end="")

def prYellow(skk): print("\033[93m {}\033[00m" .format(skk), file=sys.stderr, end="")

class Parser():
    def __init__(self, token_list: list[TokenClass], src: str, silent: bool = False):
        self.src = src
        self.token_list = token_list
        self.silent = silent
        self.main_program = None
        self.symbols_list = {"Var1": "Value1", "Var2": "Value2", "Var3": "Value3",}
        self.arithmetic_operations = [
            TokenType.SUM_OF,
            TokenType.DIFF_OF,
            TokenType.PRODUKT_OF,
            TokenType.QUOSHUNT_OF,
            TokenType.MOD_OF,
            TokenType.BIGGR_OF,
            TokenType.SMALLR_OF
        ]
        self.boolean_operations = [
            TokenType.BOTH_OF,
            TokenType.EITHER_OF,
            TokenType.WON_OF,
            TokenType.NOT,
        ]
        self.compasion_operations = [
            TokenType.BOTH_SAEM,
            TokenType.DIFFRINT,
        ]
        self.string_operations = [
            TokenType.SMOOSH
        ]
        self.mult_arity_bool = [TokenType.ALL_OF, TokenType.ANY_OF, TokenType.SMOOSH]
        self.expression_tokens = self.arithmetic_operations + self.boolean_operations + self.compasion_operations + self.string_operations + self.mult_arity_bool
        self.types = [TokenType.NUMBAR_TYPE, TokenType.NUMBR_TYPE, TokenType.YARN_TYPE, TokenType.TROOF]

        self.analyze_syntax()
    def addSymbol(self,key,value):
        self.symbols_list[key] = value

    def get_symbols(self)-> dict:
        return self.symbols_list
    
    def get_program(self) -> Program:
        return self.main_program
    
    # Returns None if token_list is empty
    def pop(self) -> (TokenClass | None):
        if len(self.token_list) == 0:
            return None
        
        return self.token_list.pop(0)
    
    def peek(self) -> (TokenClass | None):
        if len(self.token_list) == 0:
            return None
        
        return self.token_list[0]
    
    def get_code_line(self, line: int):
        code = ""
        temp_line = 1
        for c in self.src:

            if temp_line == line + 1:
                break

            if c == '\n':
                temp_line += 1
            
            if temp_line == line:
                code += c

        if code[0] == "\n":
            return code[1:]
        else:
            return code
    
    def printError(self, error: Errors, reference_token: TokenClass, context_token: TokenClass = None):
        print(f"error: {error}, from: {reference_token.line}, {reference_token.lexeme}, {reference_token.token_type}")
        if not self.silent:
            prRed("Parsing Error: ")
            match error:
                case Errors.DOUBLE_WHITESPACE:
                    print(f"Double whitespace found between two keywords on", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: Language specification specifies only a single whitespace seperating each keywords (except string literals).\n")
                case Errors.UNTERM_STR:
                    print(f"Unterminated string literal on", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: Language specification prevents multi-line string.\n")
                case Errors.UNIDENT_KEYWORD:
                    print(f"Unidentified keyword on", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                case Errors.UNEXPECTED_CHAR_TLDR:
                    print(f"Unidentified character after TLDR on", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: Place commands in a newline after TLDR.\n")
                case Errors.UNTERM_MULTILINE_COMMENT:
                    print(f"Unterminated multiline comment on", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.")
                    print(f" OBTW was found on", end="", file=sys.stderr)
                    prYellow(f"line {reference_token.error_context.line}.\n\n")
                    print(f"\t{reference_token.error_context.line} | {self.get_code_line(reference_token.error_context.line)}", file=sys.stderr)
                    print(f"\t.\n\t.\n\t.", file=sys.stderr)
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: Multiline comments are ended by 'TLDR'.\n")
                case Errors.EXPECTED_HAI:
                    print(f"Expected 'HAI' but found '{reference_token.lexeme}' instead on", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: Lolcode programs starts with 'HAI' and ends with 'KTHXBYE'.\n")
                case Errors.EXPECTED_WAZZUP:
                    print(f"Expected 'WAZZUP' but found '{reference_token.lexeme}' instead on", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: Variable declaration section should always be after HAI.\n")
                case Errors.EXPECTED_BUHBYE:
                    print(f"Expected 'BUHBYE' but found '{reference_token.lexeme}' instead on", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: Variable declaration section must be closed with 'BUHBYE'.\n")
                case Errors.EXPECTED_IHASA:
                    print(f"Unexpected token '{reference_token.lexeme}' found on", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: Variable declaration section must be closed with 'BUHBYE'\n      Declare variable using 'I HAS A <varident>'.\n")
                case Errors.EXPECTED_VARIDENT:
                    print(f"Unexpected token '{reference_token.lexeme}' found on", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: Declare variable using 'I HAS A <varident>'.\n")
                case Errors.UNEXPECTED_NEWLINE:
                    print(f"Unexpected newline at", file=sys.stderr, end="")
                    prYellow(f"line {context_token.line}.\n\n")
                    print(f"\tParsing line:", file=sys.stderr)
                    print(f"\t{context_token.line} | {self.get_code_line(context_token.line)}\n\n", file=sys.stderr)
                    print(f"\tNext token found on", end="", file=sys.stderr)
                    prYellow(f"line {reference_token.line}.\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n\n", file=sys.stderr)
                    prYellow("Tip: Lolcode commands are separated by a newline. Soft command breaks are not currently supported.\n")
                case Errors.UNEXPECTED_TOKEN:
                    print(f"Unexpected token '{reference_token.lexeme}' found on", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                case Errors.INVALID_VAR_VALUE:
                    print(f"Invalid variable value '{reference_token.lexeme}' for '{context_token.lexeme}' on", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: Supported variable values are literals, variable identifier (reference), or expression.\n") 
                case Errors.UNEXPECTED_OPERAND:
                    print(f"Unexpected operand '{reference_token.lexeme}' for {context_token.classification} found on", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: Expressions in lolcode are in prefix notation.\n")
                case Errors.INVALID_STRING_CONT_ARG:
                    print(f"Unexpected argument '{reference_token.lexeme}' for {context_token.lexeme} found on", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: Only literals and variables are allowed in string concatenation.\n")
                case Errors.INVALID_ARG_SEPARATOR:
                    print(f"Unexpected token '{reference_token.lexeme}' for '{context_token.lexeme}' operation on")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: Operations with multiple arities are separated by 'AN'.\n")
                case Errors.INCOMPLETE_EXPR:
                    print(f"Incomplete expression found for '{reference_token.lexeme}' operation on", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                case Errors.UNEXPECTED_OPERATOR:
                    print(f"Unexpected operator '{reference_token.lexeme}' for '{context_token.lexeme}' operation on")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: Bsta isng type of expression lng, pag arithmetic arithmetic lng den.\n")
                    
    def check_init_errors(self) -> bool:
        hasErrors: bool = False
        for t in self.token_list:
            if t.token_type == TokenType.UNDEFINED:
                hasErrors = True
                self.printError(t.error, t)
                continue
            
            if t.token_type == TokenType.UNTERM_STR:
                hasErrors = True
                self.printError(t.error, t)
                continue

        return hasErrors
    
    def is_literal(self, token_type: TokenType) -> bool:
        if token_type in (TokenType.YARN, TokenType.NUMBAR, TokenType.NUMBR, TokenType.TROOF, TokenType.STRING_DELIMITER, TokenType.WIN, TokenType.FAIL):
            return True
        
        return False
    
    def is_expression_starter(self, token_type: TokenType) -> bool:
        if token_type in self.expression_tokens:
            return True
        
        return False
    
    def parse_expression(self, main_op: TokenClass) -> (Expression | None):
        expression = None
        expr_type = None

        if main_op.token_type in self.arithmetic_operations:
            expression = ArithmeticExpression()
            expression.add(main_op)
            expr_type = self.arithmetic_operations
        elif main_op.token_type in self.boolean_operations:
            expression = BooleanExpression()
            expression.add(main_op)
            expr_type = self.boolean_operations
        elif main_op.token_type in self.compasion_operations:
            expression = ComparisonExpression()
            expression.add(main_op)
            expr_type = self.compasion_operations
        elif main_op.token_type in self.mult_arity_bool:
            match main_op.token_type:
                case TokenType.ANY_OF:
                    expression = AnyOfExpression(main_op, [])
                case TokenType.ALL_OF:
                    expression = AllOfExpression(main_op, [])
                case TokenType.SMOOSH:
                    expression = StringConcatenation(main_op, [])

            return self.parse_mult_arity(expression)
        
        
        an_counter = 1
        op_counter = 2

        if main_op.token_type == TokenType.NOT:
            an_counter = 0
            op_counter = 1

        while True:
            if self.peek().line != main_op.line or self.peek().token_type == TokenType.VISIBLE_CONCATENATOR:
                if op_counter != 0 or an_counter != 0:
                    self.printError(Errors.INCOMPLETE_EXPR, self.peek())
                    return None
                                    
                #check if valid expr na,, else unexpected newline
                if self.is_expr_valid(expression.expr):
                    print(expression.expr[0])
                    return expression
                
                for i in expression.expr:
                    print(str(i))
                
                print(self.is_expr_valid(expression.expr))
                self.printError(Errors.UNEXPECTED_NEWLINE, self.peek(), main_op)
                return None
            
            token = self.pop()
            print(token.lexeme)
            
            if token.token_type in self.expression_tokens:
                if token.token_type not in expr_type:
                    self.printError(Errors.UNEXPECTED_OPERATOR, token, main_op)
                    return None
                
                expression.add(token)

                if token.token_type != TokenType.NOT:
                    an_counter += 1
                    op_counter += 1     # op_counter -= 1; op_counter += 2

                continue

            if self.is_literal(token.token_type) or token.token_type == TokenType.VARIDENT:
                if token.token_type == TokenType.STRING_DELIMITER:
                    token = self.pop() # pop the literal
                    self.pop() # pop the trailing str delimiter
                
                print(f"added : {token.lexeme}")
                expression.add(token)
                op_counter -= 1

                if self.peek().line != main_op.line:
                    # has reached the end of expression
                    continue
                
                # Parse expression is called under visible
                if self.peek().token_type != TokenType.AN:
                    continue

                an = self.pop()

                if an.token_type != TokenType.AN:
                    print("hioire")
                    self.printError(Errors.INCOMPLETE_EXPR, token)
                    return None
                
                if an.line != main_op.line:
                    self.printError(Errors.UNEXPECTED_NEWLINE, token, main_op)
                    return None
                
                an_counter -= 1

                if an_counter < 0:
                    self.printError(Errors.UNEXPECTED_TOKEN, an)
                    return None
                
                continue

            self.printError(Errors.UNEXPECTED_TOKEN, token)
    

    def is_expr_valid(self, expr: list[TokenClass]) -> bool:
        operator = 0
        operand = 0
        not_count = 0

        for t in expr:
            if self.is_expression_starter(t.token_type):
                operator += 1
                if t.token_type == TokenType.NOT:
                    not_count += 1
            else:
                operand += 1

        print(f"operand: {operand}\noperator{operator}")

        if operand == (operator + 1 - not_count):
            return True
        
        return False

    # Multiple arity parsing
    # To improve HAHAHAHAAHAHA
    # String concat pa lang ang meron, dagdagan q latur
    def parse_mult_arity(self, expr: Expression):
        if isinstance(expr, StringConcatenation):
            while True:
                arg = self.pop()
                if arg.line != expr.smoosh.line:
                    self.printError(Errors.UNEXPECTED_NEWLINE, arg, expr.smoosh)
                    return None
                
                if not (self.is_literal(arg.token_type) or arg.token_type == TokenType.VARIDENT or arg.token_type == TokenType.STRING_DELIMITER):
                    print(f"{self.is_literal(arg.token_type)}")
                    self.printError(Errors.INVALID_STRING_CONT_ARG, arg, expr.smoosh)
                    return None
                
                if arg.token_type == TokenType.STRING_DELIMITER:
                    arg = self.pop()    # safe to parse string literal, as the cases were already caught in lexer
                    delim = self.pop()

                
                expr.add_args(arg)

                if self.peek().token_type != TokenType.AN:
                    print([str(x) for x in expr.args])
                    return expr

                an = self.pop()

                if an.line != expr.smoosh.line:
                    self.printError(Errors.UNEXPECTED_NEWLINE, an, expr.smoosh)
                    return None
                
                if an.token_type != TokenType.AN:
                    self.printError()
                    return None

                continue
        elif isinstance(expr, AnyOfExpression) or isinstance(expr, AllOfExpression):
            while True:
                arg = self.pop()
                if arg.line != expr.head.line:
                    self.printError(Errors.UNEXPECTED_NEWLINE, arg, expr.head)
                    return None
                
                if not (self.is_literal(arg.token_type) or arg.token_type == TokenType.VARIDENT or arg.token_type in self.boolean_operations):
                    self.printError(Errors.UNEXPECTED_TOKEN, arg)
                    return None
                
                if arg.token_type in self.boolean_operations:
                    bool_expr = BooleanExpression()
                    bool_expr.add(arg)

                    if arg.token_type == TokenType.NOT:
                        # only expecting one varident or literal

                        op = self.pop()
                        
                        if op.line != arg.line:
                            self.printError(Errors.UNEXPECTED_NEWLINE, op, arg)
                            return None
                        
                        if not (self.is_literal(op.token_type) or op.token_type == TokenType.VARIDENT):
                            self.printError(Errors.UNEXPECTED_TOKEN, op)
                            return None
                        
                        bool_expr.add(op)

                    else:
                        # Must be a normal expr
                        op1 = self.pop()

                        if op1.line != arg.line:
                            self.printError(Errors.UNEXPECTED_NEWLINE, op1, arg)
                            return None
                        
                        if not (self.is_literal(op1.token_type) or op1.token_type == TokenType.VARIDENT or op1.token_type == TokenType.NOT):
                            self.printError(Errors.UNEXPECTED_OPERAND, op, expr.head)
                            return None
                        
                        if op1.token_type == TokenType.NOT:
                            # Expect a literal or varident
                            bool_expr.add(op1)
                            val = self.pop()
                        
                            if val.line != arg.line:
                                self.printError(Errors.UNEXPECTED_NEWLINE, val, arg)
                                return None
                            
                            if not (self.is_literal(op.token_type) or op.token_type == TokenType.VARIDENT):
                                self.printError(Errors.UNEXPECTED_TOKEN, op1)
                                return None
                            
                            bool_expr.add(val)
                        else:
                            bool_expr.add(op1)

                        an = self.pop()

                        if an.line != op1.line:
                            self.printError(Errors.UNEXPECTED_NEWLINE, an, bool_expr.expr[0])
                            return None
                        
                        op2 = self.pop()

                        if op2.line != arg.line:
                            self.printError(Errors.UNEXPECTED_NEWLINE, op2, arg)
                            return None
                        
                        if not (self.is_literal(op2.token_type) or op2.token_type == TokenType.VARIDENT or op2.token_type == TokenType.NOT):
                            self.printError(Errors.UNEXPECTED_OPERAND, op2, expr.head)
                            return None
                        
                        if op2.token_type == TokenType.NOT:
                            # Expect a literal or varident
                            bool_expr.add(op2)
                            val = self.pop()
                        
                            if val.line != arg.line:
                                self.printError(Errors.UNEXPECTED_NEWLINE, val, arg)
                                return None
                            
                            if not (self.is_literal(op2.token_type) or op.token_type == TokenType.VARIDENT):
                                self.printError(Errors.UNEXPECTED_TOKEN, op2)
                                return None
                            
                            bool_expr.add(val)
                        else:
                            bool_expr.add(op2)

                    expr.add_param(bool_expr)

                if self.peek().token_type == TokenType.AN:
                    an = self.pop()

                    if an.line != expr.head.line:
                        self.printError(Errors.UNEXPECTED_NEWLINE, an, expr.head)
                        return None
                
                    continue

                if self.peek().token_type == TokenType.MKAY:
                    mkay = self.pop()

                    if mkay.line != expr.head.line:
                        self.printError(Errors.UNEXPECTED_NEWLINE, an, expr.head)
                        return None
                    
                    print([str(x) for x in expr.params])

                    for x in expr.params:
                        if isinstance(x, BooleanExpression):
                            print([str(i) for i in x.expr])
                    return expr
                
        return None
                
    def analyze_syntax(self):
        if (self.check_init_errors()):
            exit(1)

        self.main_program: Program = Program()

        hai: TokenClass = self.pop()
        if hai.token_type == TokenType.HAI:
            self.main_program.hai = hai
        else:
            self.printError(Errors.EXPECTED_HAI, hai)
            return
    
        wazzup: TokenClass = self.pop()
        if wazzup.token_type == TokenType.WAZZUP:
            self.main_program.hai = wazzup
        else:
            self.printError(Errors.EXPECTED_WAZZUP, wazzup)
            return
        
        self.main_program.variableList = VariableList(wazzup)

        # Variable delcaration checking
        while True:
            if self.peek().token_type == TokenType.BUHBYE:
                self.main_program.variableList.buhbye = self.pop()
                break

            i_has_a: TokenClass = self.pop()

            cur_line = i_has_a.line

            if i_has_a.token_type != TokenType.I_HAS_A:
                self.printError(Errors.EXPECTED_IHASA, i_has_a)
                return
            
            vari_dec = VariableDeclaration(i_has_a = i_has_a)

            varident = self.pop()
            if varident.line != cur_line:
                self.printError(Errors.UNEXPECTED_NEWLINE, varident, i_has_a)
                return
            
            if varident.token_type != TokenType.VARIDENT:
                self.printError(Errors.EXPECTED_VARIDENT, varident)
                return
            
            vari_dec.varident = varident

            if self.peek().token_type != TokenType.ITZ:
                if self.peek().line == cur_line:
                    self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
                    return
                
                self.main_program.variableList.add_variable_declaration(vari_dec)
                continue
                
            # ITZ found, must assign a value to the declaration
            itz = self.pop()
            vari_dec.itz = itz

            init_val = self.pop()
            
            if init_val.line != cur_line:
                self.printError(Errors.UNEXPECTED_NEWLINE, init_val, i_has_a)
                return
                        
            if not (self.is_literal(init_val.token_type) or self.is_expression_starter(init_val.token_type) or (init_val.token_type == TokenType.VARIDENT)):
                self.printError(Errors.INVALID_VAR_VALUE, init_val, vari_dec.varident)
                return
            
            if init_val.token_type == TokenType.STRING_DELIMITER:
                yarn = self.pop()

                # In theory, this should never get executed
                if yarn.token_type != TokenType.YARN:
                    self.printError(Errors.UNEXPECTED_TOKEN, yarn)
                    return
                
                vari_dec.value = yarn
                self.pop()
            elif init_val.token_type == TokenType.VARIDENT or self.is_literal(init_val.token_type):
                vari_dec.value = init_val
            else: # Must be an expression
                val = self.parse_expression(init_val)

                if val == None:
                    return
                
                if isinstance(val, StringConcatenation):
                    for i in val.args:
                        print(str(i))
                
                vari_dec.value = val

            if self.peek().line == cur_line:
                self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
                return
            
            self.main_program.variableList.add_variable_declaration(vari_dec)


        # Statement parsing
        while True:
            # Code does not end in BUHBYE
            if self.peek().token_type == None:
                if len(self.main_program.statementList) == 0:
                    self.printError(Errors.EXPECTED_KTHXBYE, self.main_program.variableList.buhbye)
                    return

                self.printError(Errors.EXPECTED_BUHBYE, self.main_program.statementList[-1])
                return

            # KTHXBYE encountered, meaning program should end
            if self.peek().token_type == TokenType.KTHXBYE:
                if len(self.token_list) > 1:
                    self.pop()
                    unexpected_token = self.pop()
                    self.printError(Errors.UNEXPECTED_TOKEN, unexpected_token)
                    return

                self.main_program.variableList.buhbye = self.pop()
                break
                
            if self.analyze_statement():
                continue

            return
        
        '''
        IF_MODE -> Analyzing statements inside an IF-ELSE clause, does not allow nesting if IF-ELSE
        FUNC_mode -> Analyzing statements inside a function dec, does not allow functions to be declared inside func
        SC_MODE -> Analyzing staements inside a switch case, does not allow switch case nesting
        '''
            
    def analyze_statement(self, IF_mode: bool = False, FUNC_mode = False, SC_Mode = False) -> bool:
        token = self.pop()

        # Expression statement parser
        if self.is_expression_starter(token.token_type):
            expr = self.parse_expression(token)

            if expr == None:
                return False
            
            self.main_program.add_statement(expr)

        '''
        Varident can have two possible grammars:
            - Assignment -> varident R <literal | expr>
            - Typecasting -> varident IS NOW A <type>
        '''
        if token.token_type == TokenType.VARIDENT:
            next = self.pop()
            
            if next.line != token.line:
                self.printError(Errors.UNEXPECTED_NEWLINE, next, token)
                return False

            # Assignment Statement
            if next.token_type == TokenType.R:
                value_token = self.pop()

                if value_token.line != next.line:
                    self.printError(Errors.UNEXPECTED_NEWLINE, value_token, token)
                    return False
                
                if self.is_expression_starter(value_token.token_type):
                    expression = self.parse_expression(value_token)
                    self.main_program.add_statement(AssignmentStatement(next, token, expression))
                    return True
                
                if self.is_literal(value_token.token_type):
                    self.main_program.add_statement(AssignmentStatement(next, token, value_token))
                    return True
                
                self.printError(Errors.UNEXPECTED_TOKEN, value_token)
                return False
            
            # Recasting
            if next.token_type == TokenType.IS_NOW_A:
                vartype_token = self.pop()

                if vartype_token.token_type not in self.types:
                    self.printError(Errors.UNEXPECTED_TOKEN, vartype_token)
                    return False
                
                self.main_program.add_statement(RecastStatement(token, value_token, vartype_token))
                return True

        # Typecasting
        if token.token_type == TokenType.MAEK:
            if self.peek().token_type != TokenType.VARIDENT:
                self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
                return False
                
            varident = self.pop()

            if varident.line != token.line:
                self.printError(Errors.UNEXPECTED_NEWLINE, varident, token)
                return False

            if self.peek().token_type != TokenType.A:
                self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
                return False
                
            a = self.pop()

            if a.line != token.line:
                self.printError(Errors.UNEXPECTED_NEWLINE, a, token)
                return False

            if self.peek().token_type not in self.types:
                self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
                return False
                
            type = self.pop()
            self.main_program.statementList.append(TypecastStatement(token, varident, type))
            return True
        
        '''
        Flow Control
        '''

        # #if else
        # if token.token_type == TokenType.O_RLY:
        #     if self.peek().token_type != TokenType.NEWLINE:
        #         self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
        #         return
                
        #     newline = self.pop()
        #     if self.peek().token_type != TokenType.YA_RLY:
        #         self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
        #         return
                
        #     ya_rly = self.pop()
        #     if self.peek().token_type != TokenType.NEWLINE:
        #         self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
        #         return
            
        #     newline = self.pop()
        #     if self.peek().token_type != TokenType.NO_WAI:
        #         self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
        #         return
            
        #     no_wai = self.pop()
        #     if self.peek().token_type != TokenType.NEWLINE:
        #         self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
        #         return
            
        #     newline = self.pop()
        #     if self.peek().token_type != TokenType.OIC:
        #         self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
        #         return
            
        #     oic = self.pop()
        #     if self.peek().token_type != TokenType.NEWLINE:
        #         self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
        #         return
            
        #     newline = self.pop()

        #     self.main_program.add_statement(IfElseStatement(token, ya_rly, no_wai, oic))
        #     return
        
     #switch
        # if token.token_type == TokenType.WTF:
        #     if self.peek().token_type != TokenType.NEWLINE:
        #         self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
        #         return
            
        #     newline = self.pop()
        #     if self.peek().token_type != TokenType.OMG:
        #         self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
        #         return
            
        #     omg = self.pop()
        #     if self.peek().token_type != TokenType.NEWLINE:
        #         self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
        #         return
            
        #     newline = self.pop()
        #     if self.peek().token_type != TokenType.OMGWTF:
        #         self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
        #         return
            
        #     omgwtf = self.pop()
        #     if self.peek().token_type != TokenType.NEWLINE:
        #         self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
        #         return
            
        #     newline = self.pop()
        #     if self.peek().token_type != TokenType.OIC:
        #         self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
        #         return
            
        #     oic = self.pop()
        #     if self.peek().token_type != TokenType.NEWLINE:
        #         self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
        #         return
            
        #     newline = self.pop()

        #     self.main_program.add_statement(SwitchCaseStatement(token, omg, omgwtf, oic))
        #     return

        #loop
        # if token.token_type == TokenType.IM_IN_YR:
        #     if self.peek().token_type != TokenType.VARIDENT:
        #         self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
        #         return
            
        #     varident = self.pop()
        #     # if self.peek().token_type != TokenType.NEWLINE:
        #     #     self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
        #     #     return
            
        #     # newline = self.pop()
        #     if self.peek().token_type != TokenType.UPPIN and self.peek().token_type != TokenType.NERFIN:
        #         self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
        #         return
            
        #     step = self.pop()
        #     if self.peek().token_type != TokenType.YR:
        #         self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
        #         return
            
        #     yr = self.pop()
        #     if self.peek().token_type != TokenType.VARIDENT:
        #         self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
        #         return
            
        #     counter = self.pop()
        #     # if self.peek().token_type != TokenType.NEWLINE:
        #     #     self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
        #     #     return
            
        #     # newline = self.pop()

        #     self.main_program.add_statement(LoopStatement(token, varident, step, yr, counter))
        #     return

        # input statement
        if token.token_type == TokenType.GIMMEH:
            if self.peek().token_type != TokenType.VARIDENT:
                self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
                return False
            if self.peek().line != token.line:
                self.printError(Errors.UNEXPECTED_NEWLINE, self.peek(), token)
                return False
            varident = self.pop()
            self.main_program.add_statement(InputStatement(token, varident))
            return True

        # for printing
        if token.token_type == TokenType.VISIBLE:
            print_statement = PrintStatement(token)
            while True:
                arg = self.pop()
                print(f"now parsing on visible: {arg.lexeme}")

                if arg.line != token.line:
                    self.printError(Errors.UNEXPECTED_NEWLINE, arg, token)
                    return False
                
                if not (self.is_literal(arg.token_type) or arg.token_type == TokenType.VARIDENT or self.is_expression_starter(arg.token_type)):
                    self.printError(Errors.UNEXPECTED_TOKEN, arg)
                    return False
                # string (yarn ipopop dito)

                if arg.token_type == TokenType.STRING_DELIMITER:
                    print("this is very true")
                    yarn = self.pop()
                    if yarn.token_type != TokenType.YARN:
                        self.printError(Errors.UNEXPECTED_TOKEN, yarn)
                        return False
                    
                    print_statement.args.append(yarn)
                    self.pop()
                    
                elif arg.token_type == TokenType.VARIDENT or self.is_literal(arg.token_type):
                    print_statement.args.append(arg)
                    
                elif arg.token_type in self.expression_tokens:
                    expr = self.parse_expression(arg)
                    if expr == None:
                        return False
                    
                    print_statement.args.append(expr)
                    
                if self.peek().line != token.line:
                    print(print_statement.args)
                    self.main_program.add_statement(print_statement)
                    return True
                plusSign = self.pop()

                if plusSign.token_type == TokenType.VISIBLE_CONCATENATOR:
                    continue
                else:
                    self.printError(Errors.UNEXPECTED_TOKEN, plusSign)
                    return False