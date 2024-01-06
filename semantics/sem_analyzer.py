from parser.program import Program
from semantics.symbol_table import SymbolTable
from parser.expression import *
from lexer.token_type import TokenType
from lexer.token_class import TokenClass
from misc.errors import Errors
from semantics.symbol import Symbol
from semantics.noob import Noob
from parser.variable_declaration import VariableDeclaration
from parser.io import PrintStatement, InputStatement
from parser.assignment import *
from parser.flow_control import *
from parser.functions import *
from parser.typecast import *
from typing import Any, Optional
import sys
import re
import copy
from tkinter import *

'''
The semantic analyzer requires the `Program` object produced by the parser.

The execution of statements is done here. It stops when a statement produces an error or when all of the statement has been executed.
'''

def prRed(skk): print("\033[91m {}\033[00m" .format(skk), file=sys.stderr, end="")

def prYellow(skk): print("\033[93m {}\033[00m" .format(skk), file=sys.stderr, end="")

class SemanticAnalyzer():
    def __init__(self, main_program : Program, code: str, root: Tk=None, console: Text=None) -> None:
        self.root = root    # Used to interact with the UI
        self.console = console
        self.main_program = main_program
        self.src = code
        self.silent = False
        self.sym_table = SymbolTable()  # Main symbol table of the program.

        '''
        These array declarations are used to check if which expression does the token belongs to.

        Usage:
            token.token_type in self.arithmetic_operations -> bool
        '''
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
        self.numbers = [TokenType.NUMBAR, TokenType.NUMBR]
        self.bools = [TokenType.WIN, TokenType.FAIL]
        self.types = [TokenType.NUMBAR_TYPE, TokenType.NUMBR_TYPE, TokenType.YARN_TYPE, TokenType.TROOF_TYPE]

        self.execute_program()  # Starts statement execution

    # Returns the main symbol table
    def get_sym_table(self) -> dict:
        return self.sym_table.get_sym_table()

    # Returns the line of code, given a line number
    # Used in error printing
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

    '''
    Most of these errors are runtime errors since "compile-time" errors have already been caught by the parser.
    '''
    def printError(self, error: Errors, reference_token: TokenClass, context_token: TokenClass = None, more_context: list[Any] = []):
        print(f"error: {error}, from: {reference_token.line}, {reference_token.lexeme}, {reference_token.token_type}")
        if not self.silent:
            prRed("Semantic Error: ")
            match error:
                case Errors.UNEXPECTED_OPERATOR:
                    print(f"Unexpected operator '{reference_token.lexeme}' for '{context_token.lexeme}' operation on", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: Bsta isng type of expression lng, pag arithmetic arithmetic lng den.\n")
                case Errors.INVALID_LITERAL_FOR_INT:
                    print(f"Invalid literal for integer '{reference_token.literal}' on", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: Dpat wlang decimal ang string pag iconvert s int.\n")
                case Errors.INVALID_LITERAL_FOR_FLOAT:
                    print(f"Invalid literal for integer '{reference_token.literal}' on", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: String must contain any non-numerical, non-hyphen, non-period characters.\n")
                case Errors.INVALID_OPERAND:
                    print(f"Invalid operand '{reference_token.literal}' for {context_token.lexeme} operation on", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: Noobs can only be used in boolean operations, and evaluates to false.\n")
                case Errors.CANT_TYPECAST:
                    print(f"Can't typecast '{reference_token.literal}' for {context_token.lexeme} operation on", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                case Errors.REFERENCED_UNDEFINED_VAR:
                    print(f"Referenced an undefined variable '{reference_token.lexeme}' on ", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                case Errors.DIVIDE_BY_ZERO:
                    print(f"Division by zero occured on ", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: No. You just can't.\n")
                case Errors.UNINITIALIZED_VAR:
                    print(f"Uninitialized variable '{reference_token.lexeme}' was used in an '{context_token.lexeme}' operation on", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                case Errors.CANT_RESOLVE_VALUE:
                    print(f"Can't resolve the value of the operand: '{reference_token.lexeme}' on ", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: Is this error even possible?\n")
                case Errors.UNDEFINED_VAR_FUNC:
                    print(f"Referenced an undefined variable '{reference_token.lexeme}' inside function {context_token.lexeme} on ", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: Functions have their own symbol table. It can only use the variables that was passed onto it.\n")
                case Errors.UNDEFINED_FUNCTION:
                    print(f"Called an undefined function '{reference_token.lexeme}' on ", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                case Errors.ARG_PARAM_MISMATCH:
                    # more_context = [num of params, num of args]
                    if more_context[0] > more_context[1]:
                        print(f"Missing {more_context[0] - more_context[1]} argument(s) on function call for '{reference_token.lexeme}' on ", file=sys.stderr, end="")
                    else:
                        print(f"Too many argument(s) ({more_context[1] - more_context[0]}) on function call for '{reference_token.lexeme}' on ", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\tFunction call:", file=sys.stderr)
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n\n", file=sys.stderr)
                    print(f"\tFunction declaration:", file=sys.stderr)
                    print(f"\t{context_token.line} | {self.get_code_line(context_token.line)}\n\n", file=sys.stderr)
                case Errors.RETURN_OUTSIDE_FUNC:
                    print(f"Return statement used outside a function at ", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: Return statement 'FOUND YR' could only be used inside a function declaration.\n")
                case Errors.GTFO_OUTSIDE_FUNC:
                    print(f"Empty return statement used outside a function at ", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: GTFO can only be used to terminate loops, switch-cases, or to return nothing.\n")
                case Errors.INVALID_COUNTER:
                    print(f"Invalid counter variable'{reference_token.lexeme}' used inside loop {context_token.lexeme} on ", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: Loop counter variables must be a number, or at least can be casted into a number.\n")
                case Errors.LOOP_IDENT_MISMATCH:
                    print(f"Loop identifier mismatch on loop delimiter of loop '{context_token.lexeme}' on line", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\tLoop delimiter statement:", file=sys.stderr)
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    print(f"\tLoop declaration:", file=sys.stderr)
                    print(f"\t{context_token.line} | {self.get_code_line(context_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: The indentifier found in the loop delimiter must match the one used in loop declaration.\n")
                case Errors.CANT_TYPECAST_VAR:
                    print(f"Can't typecast the value of variable '{reference_token.lexeme}' to '{context_token.lexeme}' on", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                case Errors.RECURSION_NOT_SUPPORTED:
                    print(f"Tried to call function '{reference_token.lexeme}' inside itself on", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: Recursion is not currently supported.\n")
                case Errors.TYPECASTING_NOOB:
                    print(f"Tried typecasting '{reference_token.lexeme}' on ", file=sys.stderr, end="")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: NOOB can only be implicitly typecasted into a boolean.\n")
                    
    # Same function in parser, but this time this is mostly used in expression evaluator.
    def is_literal(self, token_type: TokenType) -> bool:
        if token_type in (TokenType.YARN, TokenType.NUMBAR, TokenType.NUMBR, TokenType.WIN, TokenType.FAIL, TokenType.NOOB):
            return True
        
        return False
    
    # Accepts a TokenClass literal and returns the a typecasted value of the literal
    def cast_token_value(self, token: TokenClass, type: TokenType) -> any:
        # print(f"type: {token.token_type}, to: {type}")
        match token.token_type:
            case TokenType.NUMBR:
                match type:
                    case TokenType.NUMBR_TYPE:
                        return token.literal
                    case TokenType.NUMBAR_TYPE:
                        return float(token.literal)
                    case TokenType.YARN_TYPE:
                        return str(token.literal)
                    case TokenType.TROOF_TYPE:
                        if token.literal == 0:
                            return False
                        
                        return True
            case TokenType.NUMBAR:
                match type:
                    case TokenType.NUMBR_TYPE:
                        return int(token.literal)
                    case TokenType.NUMBAR_TYPE:
                        return token.literal
                    case TokenType.YARN_TYPE:
                        return str(token.literal)
                    case TokenType.TROOF_TYPE:
                        if token.literal == 0.0:
                            return False
                        
                        return True
            case TokenType.YARN:
                match type:
                    case TokenType.NUMBR_TYPE:
                        str_rep = token.literal
                        match = re.match(TokenType.NUMBR.value, str_rep)
                        
                        if match is not None:
                            return int(token.literal)
                        
                        self.printError(Errors.INVALID_LITERAL_FOR_INT, token)
                        return None
                    case TokenType.NUMBAR_TYPE:
                        str_rep = token.literal
                        match = re.match(TokenType.NUMBAR.value, str_rep)

                        if match is not None:
                            return float(token.literal)
                        
                        self.printError(Errors.INVALID_LITERAL_FOR_INT, token)
                        return None
                    case TokenType.YARN_TYPE:
                        return token.literal
                    case TokenType.TROOF_TYPE:
                        if token.literal == "":
                            return False
                        
                        return True
            case TokenType.WIN | TokenType.FAIL:
                match type:
                    case TokenType.NUMBR_TYPE:
                        if token.token_type == TokenType.WIN:
                            return 1
                        
                        return 0
                    case TokenType.NUMBAR_TYPE:
                        if token.token_type == TokenType.WIN:
                            return 1.0
                        
                        return 0.0
                    case TokenType.YARN_TYPE:
                        return str(token.literal)
                    case TokenType.TROOF_TYPE:
                        if token.token_type == TokenType.WIN:
                            return True

                        return False
    
    '''
    Error handling is called on the calling function, since this function does not have access to any TokenClass
    Do this after calling the function:

    casted_val = self.cast_literal_value(val.value, typecaststatement.type)

    if casted_val == None:
        self.printError(Errors.CANT_TYPECAST_VAR, typecaststatement.varident, typecaststatement.type)
        return None
    '''
    # Casts a literal value into another type
    def cast_literal_value(self, val: Any, token_type: TokenType) -> Any:
        # print(f"type of passed val = {type(val)}")
        if val == Noob.NOOB:
            if token_type == TokenType.TROOF_TYPE:
                return False
            if token_type == TokenType.NUMBAR_TYPE:
                return 0.0
            if token_type == TokenType.NUMBR_TYPE:
                return 0
            return None

        if type(val) == int:
            match token_type:
                case TokenType.NUMBR_TYPE:
                    return val
                case TokenType.NUMBAR_TYPE:
                    return float(val)
                case TokenType.TROOF_TYPE:
                    if val == 0:
                        return False
                    
                    return True
                case TokenType.YARN_TYPE:
                    return str(val)
        elif type(val) == float:
            match token_type:
                case TokenType.NUMBR_TYPE:
                    return int(val)
                case TokenType.NUMBAR:
                    return val
                case TokenType.TROOF_TYPE:
                    if val == 0.0:
                        return False
                    
                    return True
                case TokenType.YARN_TYPE:
                    return str(val)
        elif type(val) == str:
            match token_type:
                case TokenType.NUMBR_TYPE:
                    match = re.match(TokenType.NUMBR.value, val)
                        
                    if match is not None:
                        return int(val)
                    
                    return None
                case TokenType.NUMBAR_TYPE:
                    match = re.match(TokenType.NUMBAR.value, val)

                    if match is not None:
                        return float(val)
                    
                    return None
                case TokenType.YARN_TYPE:
                    return val
                case TokenType.TROOF_TYPE:
                    if val == "":
                        return False
                    
                    return True
        elif type(val) == bool:
            match token_type:
                case TokenType.NUMBR_TYPE:
                    if val:
                        return 1
                    
                    return 0
                case TokenType.NUMBAR_TYPE:
                    if val:
                        return 1.0
                    
                    return 0.0
                case TokenType.YARN_TYPE:
                    if val:
                        return "WIN"
                    
                    return "FAIL"
                case TokenType.TROOF_TYPE:
                    return val

    # Extracts a number literal from the given parameter. Accepts either a tokenclass (variable or literal), or a number (int or float).
    'See semantics/README.md for a detailed explanation.'
    def unwrap_num(self, op: (TokenClass | int | float), tokens: list[TokenClass], FN_mode: bool = False, st: SymbolTable = None) -> (float | int | None):
        # If type(op) is number, just return it.
        if type(op) == int or type(op) == float:
            return op
        
        # Can't implicitly typecast noob into number.
        if op.token_type == TokenType.NOOB:
            self.printError(Errors.TYPECASTING_NOOB, op)
            return None
        
        # op is either varident or IT
        if op.token_type in (TokenType.VARIDENT, TokenType.IT):
            op_val = None

            if FN_mode:
                    op_val = st.retrieve_val(op.lexeme)
            else: op_val: Symbol = self.sym_table.retrieve_val(op.lexeme)

            if op_val == None:
                self.printError(Errors.REFERENCED_UNDEFINED_VAR, op)
                return None
            
            # Can't implicitly typecast NOOB to number
            if op_val.value == Noob.NOOB:
                self.printError(Errors.TYPECASTING_NOOB, op)
                return None
            
            # Implicitly typecast value to number
            if op_val.type not in self.numbers:
                if re.match(TokenType.NUMBR.value, op_val.value):
                    return int(op_val.value)
                elif re.match(TokenType.NUMBAR.value, op_val.value):
                    return float(op_val.value)
                else:
                    # Must be a troof
                    if op_val.type == TokenType.WIN:
                        return 1
                    elif op_val.type == TokenType.FAIL:
                        return 0
                    elif op_val.type == TokenType.NOOB:
                        self.printError(Errors.INVALID_OPERAND, op, tokens[-1])
                        return None

                    # Invalid string
                    self.printError(Errors.CANT_TYPECAST, op, tokens[-1])
                    return None    
            elif op_val.type in self.numbers:
                # Value is already a number
                return op_val.value
        
        # Literal is not a number, implicitly typecast to numbers
        elif op.token_type not in self.numbers:
            # Match first if integer, since 
            if re.match(TokenType.NUMBR.value, op.lexeme):
                return self.cast_token_value(op, TokenType.NUMBR_TYPE)
            elif re.match(TokenType.NUMBAR.value, op.lexeme):
                return self.cast_token_value(op, TokenType.NUMBAR_TYPE)
            else:
                # Must be troof
                if op.token_type == TokenType.WIN:
                    return 1
                elif op.token_type == TokenType.FAIL:
                    return 0
                elif op.token_type == TokenType.NOOB:
                    self.printError(Errors.UNINITIALIZED_VAR, op, tokens[-1])
                    return None

                # Invalid string
                self.printError(Errors.CANT_TYPECAST, op, tokens[-1])
                return None
        elif op.token_type in self.numbers:
            return op.literal
            
        return None
    
    # Extracts a boolean literal from the given parameter. Accepts either a tokenclass (variable or literal), or a boolean.
    'See semantics/README.md#retrieving-values-of-operands for a detailed explanation.'
    def unwrap_bool(self, op: (TokenClass | bool), FN_mode: bool = False, st: SymbolTable = None) -> (bool | None):
        # op is already bool, return
        if type(op) == bool:
            return op
        
        # Noob can only be implicitly typecasted into bool. 
        if op.token_type == TokenType.NOOB:
            return False    # Noob is falsy
        
        # op either literal or IT
        if op.token_type in (TokenType.VARIDENT, TokenType.IT):
            op_val = None
            if FN_mode:
                op_val = st.retrieve_val(op.lexeme)
            else: op_val: Symbol = self.sym_table.retrieve_val(op.lexeme)

            if op_val == None:
                self.printError(Errors.REFERENCED_UNDEFINED_VAR, op)
                return None
            
            # Noob can only be implicitly typecasted into bool. 
            if op_val.value == Noob.NOOB:
                return False
                        
            # Implicitly typecast value to bool
            if op_val.type not in self.bools:
                if op_val.type == TokenType.NUMBAR or op_val.type == TokenType.NUMBR:
                    if op_val.value == 0:
                        return False
                    else: return True
                elif op_val.type == TokenType.YARN:
                    if op_val.value == "":
                        return False
                    else: return True
                elif op_val.type == TokenType.NOOB:
                    return False
                
            if op_val.type == TokenType.WIN:
                return True
            
            return False
        
        # Implicitly typecast literal into bool
        elif op.token_type not in self.bools:
            if op.token_type == TokenType.NUMBAR or op.token_type == TokenType.NUMBR:
                if op.literal == 0:
                    return False
                else: return True
            elif op.token_type == TokenType.YARN:
                if op.literal == "":
                    return False
                else: return True
            elif op.token_type == TokenType.NOOB:
                return False
        elif op.token_type in self.bools:
            # Change TROOF into python representation of boolean
            if op.token_type == TokenType.WIN:
                return True
            else: return False
        else:
            return None
    
    # Extracts a value without typecasting
    def unwrap_no_cast(self, op: (TokenClass | int | float | bool | str), FN_mode, st: SymbolTable) -> Any:
        if isinstance(op, (int, float, bool, str)):
            return op

        if op.token_type in (TokenType.VARIDENT, TokenType.IT):
            op_val = None

            if FN_mode:
                op_val = st.retrieve_val(op.lexeme)
            else: op_val: Symbol = self.sym_table.retrieve_val(op.lexeme)

            if op_val == None:
                self.printError(Errors.REFERENCED_UNDEFINED_VAR, op)
                return None

            return op_val.value
        
        if self.is_literal(op.token_type):
            # Convert TROOF into pytthon representation of v
            if op.token_type == TokenType.WIN:
                return True
            
            if op.token_type == TokenType.FAIL:
                return False
            
            return op.literal
        
        if op.token_type == TokenType.NOOB:
            return Noob.NOOB
        
        self.printError(Errors.CANT_RESOLVE_VALUE, op)
        return None


            
    def execute_nesting_expression(self, expression: Expression, FN_mode: bool, st: SymbolTable) -> Optional[Any]: # Returns the value of the expression
        stack: list[TokenClass] = []
        
        tokens: list[TokenClass] = copy.deepcopy(expression.expr) # Copy the tokens to avoid modifying the original tokens
        tokens.reverse()   # Reverse the tokens to make it easier to pop from the stack

        expr_type = None
        if tokens[-1].token_type in self.arithmetic_operations:
            expr_type = self.arithmetic_operations
        elif tokens[-1].token_type in self.boolean_operations:
            expr_type = self.boolean_operations
        elif tokens[-1].token_type in self.compasion_operations:
            expr_type = self.expression_tokens

        for t in tokens: 
            # print(f"now parsing : {t.lexeme}")
            if t.token_type in self.expression_tokens: # If token is an operator
                if t.token_type not in expr_type: # If token is not an operator for the current expression
                    self.printError(Errors.UNEXPECTED_OPERATOR, t, tokens[-1]) # Print error
                    return None
                
                match t.token_type: # Matching of the token type
                    # Arithmetic Operations
                    case TokenType.SUM_OF: # when addition
                        'Subtraction'
                        # Pop from the stack
                        op1: (TokenClass | int | float) = stack.pop()
                        op2: (TokenClass | int | float)  = stack.pop()

                        # Unwrap values as num
                        op1_val = self.unwrap_num(op1, tokens, FN_mode, st)
                        if op1_val == None:
                            return None
                        
                        op2_val = self.unwrap_num(op2, tokens, FN_mode, st)
                        if op2_val == None:
                            return None
                        
                        # Let python do the float typecasting
                        result = op1_val + op2_val
                        stack.append(result)
                    
                    case TokenType.DIFF_OF: # when subtraction
                        'Subtraction'
                        # Pop from the stack
                        op1: (TokenClass | int | float) = stack.pop()
                        op2: (TokenClass | int | float)  = stack.pop()

                        # Unwrap values as num
                        op1_val = self.unwrap_num(op1, tokens, FN_mode, st)
                        if op1_val == None:
                            return None
                        
                        op2_val = self.unwrap_num(op2, tokens, FN_mode, st)
                        if op2_val == None:
                            return None
                        
                        # Let python do the float typecasting
                        result = op1_val - op2_val
                        stack.append(result)
                    
                    case TokenType.PRODUKT_OF: # when multiplication
                        'Multiplication'
                        # Pop from the stack
                        op1: (TokenClass | int | float) = stack.pop()
                        op2: (TokenClass | int | float)  = stack.pop()

                        # Unwrap values as num
                        op1_val = self.unwrap_num(op1, tokens, FN_mode, st)
                        if op1_val == None:
                            return None
                        
                        op2_val = self.unwrap_num(op2, tokens, FN_mode, st)
                        if op2_val == None:
                            return None
                        
                        # Let python do the float typecasting
                        result = op1_val * op2_val
                        stack.append(result)
                    
                    case TokenType.QUOSHUNT_OF: #when division
                        'Division'
                        # Pop from the stack
                        op1: (TokenClass | int | float) = stack.pop()
                        op2: (TokenClass | int | float)  = stack.pop()

                        # Unwrap values as num
                        op1_val = self.unwrap_num(op1, tokens, FN_mode, st)
                        if op1_val == None:
                            return None
                        
                        op2_val = self.unwrap_num(op2, tokens, FN_mode, st)
                        if op2_val == None:
                            return None
                        
                        if op2_val == 0:
                            self.printError(Errors.DIVIDE_BY_ZERO, t)
                            return None

                        
                        # Let python do the float typecasting
                        result = op1_val / op2_val

                        if type(op1_val) == int and type(op2_val) == int:
                            if result.is_integer():
                                result = int(result)

                        stack.append(result)
                    
                    case TokenType.MOD_OF: #when modulo
                        'Modulo'
                        # Pop from the stack
                        op1: (TokenClass | int | float) = stack.pop()
                        op2: (TokenClass | int | float)  = stack.pop()

                        # Unwrap values as num
                        op1_val = self.unwrap_num(op1, tokens, FN_mode, st)
                        if op1_val == None:
                            return None
                        
                        op2_val = self.unwrap_num(op2, tokens, FN_mode, st)
                        if op2_val == None:
                            return None
                        
                        # Let python do the float typecasting
                        result = op1_val % op2_val
                        stack.append(result)

                    case TokenType.BIGGR_OF: #when maximum
                        'Max'
                        # Pop from the stack
                        op1: (TokenClass | int | float) = stack.pop()
                        op2: (TokenClass | int | float)  = stack.pop()

                        # Unwrap values as num
                        op1_val = self.unwrap_num(op1, tokens, FN_mode, st)
                        if op1_val == None:
                            return None
                        
                        op2_val = self.unwrap_num(op2, tokens, FN_mode, st)
                        if op2_val == None:
                            return None
                        
                        # Let python do the float typecasting
                        result = max(op1_val, op2_val)
                        stack.append(result)

                    case TokenType.SMALLR_OF: #when minimum
                        'Min'
                        # Pop from the stack
                        op1: (TokenClass | int | float) = stack.pop()
                        op2: (TokenClass | int | float)  = stack.pop()

                        # Unwrap values as num
                        op1_val = self.unwrap_num(op1, tokens, FN_mode, st)
                        if op1_val == None:
                            return None
                        
                        op2_val = self.unwrap_num(op2, tokens, FN_mode, st)
                        if op2_val == None:
                            return None
                        
                        # Let python do the float typecasting
                        result = min(op1_val, op2_val)
                        stack.append(result)

                    case TokenType.BOTH_OF: #when and
                        'And'
                        op1: (TokenClass | str) = stack.pop()
                        op2: (TokenClass | str)  = stack.pop()

                        op1_val = self.unwrap_bool(op1, FN_mode, st)
                        if op1_val == None:
                            return None
                        
                        op2_val = self.unwrap_bool(op2, FN_mode, st)
                        if op2_val == None:
                            return None
                                                                        
                        # Unwrap always return a True or False, so it is safe to do bool operations
                        result = op1_val and op2_val
                        stack.append(result)

                    case TokenType.EITHER_OF: #when either
                        'Or'
                        op1: (TokenClass | str) = stack.pop()
                        op2: (TokenClass | str)  = stack.pop()

                        op1_val = self.unwrap_bool(op1, FN_mode, st)
                        
                        if op1_val == None:
                            return None
                        
                        op2_val = self.unwrap_bool(op2, FN_mode, st)
                        if op2_val == None:
                            return None
                        
                        # Unwrap always return a True or False, so it is safe to do bool operations
                        result = op1_val or op2_val
                        stack.append(result)

                    case TokenType.WON_OF: #when xor
                        'XOR'
                        op1: (TokenClass | str) = stack.pop()
                        op2: (TokenClass | str)  = stack.pop()

                        op1_val = self.unwrap_bool(op1, FN_mode, st)
                        if op1_val == None:
                            return None
                        
                        op2_val = self.unwrap_bool(op2, FN_mode, st)
                        if op2_val == None:
                            return None
                        
                        # Unwrap always return a True or False, so it is safe to do bool operations
                        result = op1_val ^ op2_val
                        stack.append(result)

                    case TokenType.NOT: #when not
                        '!'
                        op1: (TokenClass | str) = stack.pop()

                        op1_val = self.unwrap_bool(op1, FN_mode, st)
                        if op1_val == None:
                            return None
                        
                        result = not op1_val
                        stack.append(result)

                    # Comparison 

                    case TokenType.BOTH_SAEM: #when == or same
                        '=='

                        op1 = stack.pop()
                        op2 = stack.pop()

                        op1_val = self.unwrap_no_cast(op1, FN_mode, st)
                        if op1_val == None:
                            return None
                        
                        op2_val = self.unwrap_no_cast(op2, FN_mode, st)
                        if op2_val == None:
                            return None
                        
                        result = op1_val == op2_val
                        stack.append(result)

                    case TokenType.DIFFRINT: #when != or different
                        '!='

                        op1 = stack.pop()
                        op2 = stack.pop()

                        op1_val = self.unwrap_no_cast(op1, FN_mode, st)
                        if op1_val == None:
                            return None
                        
                        op2_val = self.unwrap_no_cast(op2, FN_mode, st)
                        if op2_val == None:
                            return None
                        
                        result = op1_val != op2_val
                        stack.append(result)
            else:               # If token is an operand
                stack.append(t) 

        return stack[0]
    
    # Extracts a string literal from the given parameter. Accepts either a tokenclass (variable or literal), or a string.
    'See semantics/README.md#retrieving-values-of-operands for a detailed explanation.'
    def unwrap_str(self, op: TokenClass, FN_mode: bool = False, st: SymbolTable = None) -> str:
        if self.is_literal(op.token_type):
            return str(op.literal)
        
        # Can't implicitly typecast noob into str
        if op.token_type == TokenType.NOOB: # If token is noob
            self.printError(Errors.TYPECASTING_NOOB, op)
            return None
        
        if op.token_type in (TokenType.VARIDENT, TokenType.IT): # If token is varident or IT
            op_val = None

            if FN_mode: 
                op_val = st.retrieve_val(op.lexeme)
            else: op_val = self.sym_table.retrieve_val(op.lexeme)

            if op_val == None:
                self.printError(Errors.REFERENCED_UNDEFINED_VAR, op)
                return None
            
            if op_val == Noob.NOOB:
                self.printError(Errors.TYPECASTING_NOOB, op)
                return None
            
            if type(op_val.value) == bool:
                if op_val.value:
                    return "WIN"

                return "FAIL"
            
            return str(op_val.value)
    
    # Evaluates expressions with infinite arity, produces a literal
    def execute_inf_arity_expression(self, expr: (AnyOfExpression | AllOfExpression | StringConcatenation), FN_mode: bool = False, st: SymbolTable = None) -> Optional[str | bool]:
        # String concatenation
        if isinstance(expr, StringConcatenation): # If expression is string concatenation 
            str_buffer = ""
            for a in expr.args: # For each argument in the string concatenation expression 
                arg_val = self.unwrap_str(a, FN_mode, st) # Unwrap the string literal 

                if arg_val == None: # If error occured while unwrapping, just return none 
                    return None
                
                str_buffer += arg_val # Concatenate the string

            return str_buffer
        
        # Anyof returns True immediately once True is encountered
        if isinstance(expr, AnyOfExpression): # If expression is anyof 
            for a in expr.params: # For each argument in the anyof expression 
                if isinstance(a, BooleanExpression):  # If argument is a boolean expression
                    result = self.evaluate_expression(a, FN_mode, st)

                    if result == None:
                        return None
                    
                    if result == True:
                        return True
                    
                    continue

                if isinstance(a, TokenClass): # If argument is a token class
                    param_val = self.unwrap_bool(a, FN_mode, st)

                    if param_val == None:
                        return None
                                            
                    if param_val == True:
                        return True
                    
                    continue
        
            return False # If no true is encountered, return false
        
        # All of returns False once falsy value is encountered
        if isinstance(expr, AllOfExpression): # If expression is allof
            for a in expr.params:
                if isinstance(a, BooleanExpression): # If argument is a boolean expression
                    result = self.evaluate_expression(a, FN_mode, st)

                    if result == None:
                        return None
                    
                    if result == False:
                        return False
                    
                    continue

                if isinstance(a, TokenClass): # If argument is a token class
                    param_val = self.unwrap_bool(a, FN_mode, st)

                    if param_val == None:
                        return None
                    
                    if param_val == False:
                        return False
                    
                    continue

            return True

        return None

    # A wrapper function for the expression evaluation
    def evaluate_expression(self, expr: Expression, FN_mode = False, st: SymbolTable = None) -> Optional[Any]: # Returns the value of the expression 
        if isinstance(expr, AnyOfExpression) or isinstance(expr, AllOfExpression) or isinstance(expr, StringConcatenation): # If expression is anyof, allof, or string concatenation
            return self.execute_inf_arity_expression(expr, FN_mode, st) # Evaluate the expression with infinite arity
        
        return self.execute_nesting_expression(expr, FN_mode, st) # Evaluate the expression with nesting
    
    # Returns the type of the passed value
    def get_type(self, val: any) -> TokenType:
        if type(val) == bool:
            if val:
                return TokenType.WIN
            
            return TokenType.FAIL
        elif type(val) == int:
            return TokenType.NUMBR
        elif type(val) == float:
            return TokenType.NUMBAR
        elif type(val) == str:
            return TokenType.YARN
        elif val == Noob.NOOB:
            return TokenType.NOOB
    
    # Converts a literal to bool, will do implicit typecasting
    def literal_to_bool(self, val: Any) -> bool: #
        if val == Noob.NOOB:
            return False

        if type(val) == bool: # If value is already a boolean, just return it
            return val
        
        if type(val) == int or type(val) == float: # If value is a number, return true if not 0, else return false
            if val == 0:
                return False
            
            return True
        
        if type(val) == str: # If value is a string, return true if not empty, else return false
            if val == "":
                return False
            
            return True
    
    # Converts a literal to number, will do implicit typecasting 
    def literal_to_num(self, val: any) -> (int | float):
        if val == Noob.NOOB:
            return None

        if type(val) == bool:
            if val:
                return 1
            return 0
        
        if type(val) == int or type(val) == float:
            return val
        
        if type(val) == str:
            # Check if integer first
            match = re.match(TokenType.NUMBR.value, val)
            if match is not None:
                return int(val)
            
            # Not integer, must be float?
            match = re.match(TokenType.NUMBR.value, val)
            if match is not None:
                return float(val)
            
            # Str can't be casted into a number, return none instead. Can't print error statement here
            # since there is no token
            return None
        
    # Main program execution
    def execute_program(self):
        # Variable declaration execution
        variable_declarations: list[VariableDeclaration] = self.main_program.variableList.variable_declarations

        # Evaluate through all the variable declaration first, then evaluate their assigned value if there is any
        for v in variable_declarations:
            # Uninitialized value
            if v.itz == None:
                self.sym_table.add_symbol(v.varident.lexeme, Symbol(Noob.NOOB, TokenType.NOOB))
                continue

            # Else, itz must be present so it needs to be evaluated
            val = v.value
            
            # Either a literal or a vaariable
            if type(val) == TokenClass:
                if val.token_type in (TokenType.WIN, TokenType.FAIL):
                    bool_val = True if v.value.token_type == TokenType.WIN else False
                    self.sym_table.add_symbol(v.varident.lexeme, Symbol(bool_val, val.token_type))
                    continue

                self.sym_table.add_symbol(v.varident.lexeme, Symbol(val.literal, val.token_type))

            # Value is an expression, evaluate it and store result into variable
            elif isinstance(val, Expression):
                result = self.evaluate_expression(v.value)

                if result == None:
                    return None
                
                expr_type = self.get_type(result)

                self.sym_table.add_symbol(v.varident.lexeme, Symbol(result, expr_type))
                continue
        
        self.sym_table.__print_sym__()

        # Initial symbol table is done, proceed to statement parsing
        for s in self.main_program.statementList:
            # Will continue execution until it returns None
            if (self.execute_statement(s, parent_sym_table=self.sym_table)):
                continue
            

            return None
        
        self.sym_table.__print_sym__()


    '''
    execute_statement contains all the semantic implementation of all statements. Some implementations also call execute_statements as they have to execute their own code blocks.
    See '/semantics/README.md' for a more detailed explanation.

    FUNC_mode -> execute statement inside function, modify function's symbol table instead of the main sym table
    '''
    def execute_statement(self, statement: Statement, FUNC_mode = False, sym_table: SymbolTable = None, funcident: TokenClass = None, parent_sym_table: SymbolTable = None) -> bool:
        # Visible
        if isinstance(statement, PrintStatement):
            output_buffer = ""

            # Iterate through all the arguments of the statement
            for args in statement.args:
                # Argument is expression, evaluate the value and append the result to the output buffer
                if isinstance(args, Expression):
                    result = self.evaluate_expression(args, FUNC_mode, sym_table)

                    if result == None:
                        return None
                    
                    # String representation of bool
                    if type(result) == bool:
                        if result:
                            output_buffer += "WIN"
                        else:
                            output_buffer += "FAIL"
                    else:
                        output_buffer += str(result)

                # Could either be varident or literal
                if type(args) == TokenClass:
                    # A varident
                    if args.token_type in (TokenType.VARIDENT, TokenType.IT):
                        retrieved_val = None

                        # Retrieve value from symbol table
                        if FUNC_mode:
                            retrieved_val = sym_table.retrieve_val(args.lexeme)
                        else:
                            retrieved_val = self.sym_table.retrieve_val(args.lexeme)

                        if retrieved_val == None:
                            if FUNC_mode:
                                self.printError(Errors.UNDEFINED_VAR_FUNC, args, funcident)
                                return None

                            self.printError(Errors.REFERENCED_UNDEFINED_VAR, args)
                            return None
                        
                        # String representation of NOOB
                        if retrieved_val.value == Noob.NOOB:
                            output_buffer += "NOOB"
                            continue
                        
                        # String representation of booleans
                        if retrieved_val.type in (TokenType.WIN, TokenType.FAIL):
                            if retrieved_val.type == TokenType.WIN:
                                output_buffer += "WIN"
                            
                            if retrieved_val.type == TokenType.FAIL:
                                output_buffer += "FAIL"

                            continue
                        
                        output_buffer += str(retrieved_val.value)
                    else:
                        # A literal
                        if args.token_type == TokenType.NOOB:
                            self.printError(Errors.TYPECASTING_NOOB, args)
                            return None

                        output_buffer += self.cast_token_value(args, TokenType.YARN_TYPE)

                
            output_buffer += '\n'
                
            output_buffer = output_buffer.replace('\\n', '\n').replace('\\t', '\t')
            print(output_buffer, end="")
            return True

        # Input
        if isinstance(statement, InputStatement):
            if FUNC_mode:
                if not sym_table.indentifier_exists(statement.varident.lexeme):
                    self.printError(Errors.UNDEFINED_VAR_FUNC, statement.varident, funcident)
                    return None
            elif not self.sym_table.indentifier_exists(statement.varident.lexeme):
                self.printError(Errors.REFERENCED_UNDEFINED_VAR, statement.varident)
                return None

            input_buffer = input()

            if FUNC_mode:
                sym_table.modify_symbol(statement.varident.lexeme, Symbol(input_buffer, TokenType.YARN))
                return True
            
            self.sym_table.modify_symbol(statement.varident.lexeme, Symbol(input_buffer, TokenType.YARN))
            return True
        
        # Implicit IT Declaration
        if isinstance(statement, Expression):
            result = self.evaluate_expression(statement, FUNC_mode, sym_table)
            if result == None:
                return None
            
            if FUNC_mode:
                sym_table.set_IT(Symbol(result, self.get_type(result)))
                return True
            
            self.sym_table.set_IT(Symbol(result, self.get_type(result)))
            return True
        
        # Implicit IT assignment
        if isinstance(statement, ImplicitITAssignment):
            if isinstance(statement.val, Expression):
                result = self.evaluate_expression(statement.val, FUNC_mode, sym_table)
                if result == None:
                    return None
                
                if FUNC_mode:
                    sym_table.set_IT(Symbol(result, self.get_type(result)))
                    return True
                
                self.sym_table.set_IT(Symbol(result, self.get_type(result)))
                return True
            
            if isinstance(statement.val, TokenClass):
                val = self.unwrap_no_cast(statement.val, FUNC_mode, sym_table)
                if val == None:
                    return None
                
                if FUNC_mode:
                    sym_table.set_IT(Symbol(result, self.get_type(result)))
                    return True

                self.sym_table.set_IT(Symbol(val, self.get_type(val)))
                return True
            
        # Switch case
        if isinstance(statement, SwitchCaseStatement):
            it_sym = None

            if FUNC_mode:
                it_sym = sym_table.get_IT()
            else:
                it_sym = self.sym_table.get_IT()

            it_val = it_sym.value

            case = statement.default_case.index

            for c in statement.cases:
                if it_val == self.unwrap_no_cast(c.key, FUNC_mode, sym_table):
                    case = c.index
                    break

            for s in statement.statements[case:]:
                if isinstance(s, Terminator):
                    break

                if self.execute_statement(s, FUNC_mode, sym_table, funcident):
                    continue
                else:
                    return None
                
            return True
        
        # If Then Statement
        if isinstance(statement, IfElseStatement):
            it_sym = None

            if FUNC_mode:  # this is for the function
               it_sym = sym_table.get_IT()  # get the symbol table of the function
            else:
                it_sym = self.sym_table.get_IT()   # get the original 

            it_val = self.literal_to_bool(it_sym.value)

            if it_val == True: # this is for the true case
                for s in statement.true_statements:
                    if self.execute_statement(s, FUNC_mode, sym_table, funcident, parent_sym_table):
                        continue
                    else:
                        return None
                
                return True
            # for the else case
            for s in statement.false_statements:  # run through the statements of else statement
                if isinstance(s, Terminator):
                    break

                if self.execute_statement(s, FUNC_mode, sym_table, funcident, parent_sym_table):
                    continue
                else:
                    return None
            
            return True
        
        # Function Call
        if isinstance(statement, FunctionCallStatement):
            # Check first if function exists
            if not self.main_program.func_table.is_func_defined(statement.func_ident.lexeme):
                self.printError(Errors.UNDEFINED_FUNCTION, statement.func_ident)
                return None
            
            fn = self.main_program.func_table.retrieve_func(statement.func_ident.lexeme)

            if FUNC_mode:
                if fn.funcident.lexeme == funcident.lexeme:
                    self.printError(Errors.RECURSION_NOT_SUPPORTED, statement.i_iz)
                    return None

            if len(fn.params) != len(statement.args):
                self.printError(Errors.ARG_PARAM_MISMATCH, statement.func_ident, fn.funcident, [len(fn.params), len(statement.args)])
                return None
            
            args_val = []

            for a in statement.args:
                if isinstance(a, Expression):
                    result = self.evaluate_expression(a, FUNC_mode, sym_table)

                    if result == None:
                        return None
                    
                    args_val.append(result)

                if isinstance(a, TokenClass):
                    a_val = self.unwrap_no_cast(a, FUNC_mode, sym_table)

                    if a_val == None:
                        return None
                    
                    args_val.append(a_val)
            
            # Add the arguments into function's symbol table
            counter = 0
            for p in fn.params:
                fn.sym_table.add_symbol(p.lexeme, Symbol(args_val[counter], self.get_type(args_val[counter])))
                counter += 1

            # Execute function statements
            for s in fn.statements:
                ret =  self.execute_statement(s, FUNC_mode=True, sym_table=fn.sym_table, funcident=fn.funcident, parent_sym_table=parent_sym_table)
                
                if ret:
                    continue
                elif ret == None:
                    return None
                elif ret == False:
                    return True
                    
            parent_sym_table.set_IT(Symbol(Noob.NOOB, TokenType.NOOB))
            return True
        
        # Function return
        if isinstance(statement, FunctionReturn):
            if not FUNC_mode:
                self.printError(Errors.RETURN_OUTSIDE_FUNC, statement.ret_keyword)
                return None
            
            ret_val = None

            if isinstance(statement.return_val, Expression):
                ret_val = self.evaluate_expression(statement.return_val, FUNC_mode, sym_table)

                if ret_val == None:
                    return None
                
                parent_sym_table.set_IT(Symbol(ret_val, self.get_type(ret_val)))
                return False
            
            if isinstance(statement.return_val, TokenClass):
                ret_val = self.unwrap_no_cast(statement.return_val, FUNC_mode, sym_table)

                if ret_val == None:
                    return None
                
                parent_sym_table.set_IT(Symbol(ret_val, self.get_type(ret_val)))
                return False
            
        if isinstance(statement, Terminator):
            if not FUNC_mode:
                self.printError(Errors.GTFO_OUTSIDE_FUNC, statement.gtfo)
                return None
            
            parent_sym_table.set_IT(Symbol(Noob.NOOB, TokenType.NOOB))
            return False
        
        # Assignment Statement 
        if isinstance(statement, AssignmentStatement):
            if isinstance(statement.source, Expression):  # this is for the expression
                result = self.evaluate_expression(statement.source, FUNC_mode, sym_table) # evaluate the given expression

                if result == None:
                    return None
                
                if FUNC_mode:  # this is the case if we are ins
                    sym_table.modify_symbol(statement.destination.lexeme, Symbol(result, self.get_type(result)))
                    return True
                
                self.sym_table.modify_symbol(statement.destination.lexeme, Symbol(result, self.get_type(result)))
                return True
            
            if isinstance(statement.source, TokenClass): # this is for the token class
                val = self.unwrap_no_cast(statement.source, FUNC_mode, sym_table) # unwrap the value

                if val == None:
                    return None
                
                if FUNC_mode:
                    sym_table.modify_symbol(statement.destination.lexeme, Symbol(val, self.get_type(val))) # modify the symbol table
                    return True
                
                self.sym_table.modify_symbol(statement.destination.lexeme, Symbol(val, self.get_type(val))) 
                return True
            
            if isinstance(statement.source, TypecastStatement): # this is for the typecast statement
                val = self.unwrap_no_cast(statement.destination, FUNC_mode, sym_table) # unwrap the value

                if val == None:
                    return None
                
                cast_type = statement.source.type

                if val == Noob.NOOB and cast_type.token_type != TokenType.TROOF_TYPE: # this is for the case if the value is noob
                    self.printError(Errors.CANT_TYPECAST_VAR, val, cast_type) 
                    return None
                
                casted_val = self.cast_literal_value(val, cast_type.token_type) # cast the value

                if casted_val == None: # this is for the case if the value is not castable
                    self.printError(Errors.CANT_TYPECAST_VAR, val, cast_type)
                    return None
                
                if FUNC_mode: # this is for the function
                    sym_table.modify_symbol(statement.destination.lexeme, Symbol(casted_val, self.get_type(casted_val)))
                    return True
                
                self.sym_table.modify_symbol(statement.destination.lexeme, Symbol(casted_val, self.get_type(casted_val)))
                return True

            
        # Typecasting 
        if isinstance(statement, TypecastStatement): # this is for the typecast statement
            if FUNC_mode: # this is for the function
                if not sym_table.indentifier_exists(statement.varident.lexeme): # check if the variable is declared
                    self.printError(Errors.UNDEFINED_VAR_FUNC, statement.varident, funcident) 
                    return None
            else: # this is for the main program
                if not self.sym_table.indentifier_exists(statement.varident.lexeme): # check if the variable is declared
                    self.printError(Errors.REFERENCED_UNDEFINED_VAR, statement.varident)
                    return None

            val = None
            
            # Retrieve val from symbol table
            if FUNC_mode: 
                val = sym_table.retrieve_val(statement.varident.lexeme)
            else:
                val = self.sym_table.retrieve_val(statement.varident.lexeme)

            if val == None: 
                self.printError(Errors.REFERENCED_UNDEFINED_VAR, statement.varident)
                return None
            
            if (val.value == Noob.NOOB) and statement.type.token_type != TokenType.TROOF_TYPE:
                self.printError(Errors.CANT_TYPECAST_VAR, statement.varident, statement.type)
                return None
            
            casted_val = self.cast_literal_value(val.value, statement.type.token_type)

            if casted_val == None:
                self.printError(Errors.CANT_TYPECAST_VAR, statement.varident, statement.type)
                return None
            
            if FUNC_mode:
                sym_table.modify_symbol(statement.varident.lexeme, Symbol(casted_val, self.get_type(casted_val)))
                return True
            
            self.sym_table.modify_symbol(statement.varident.lexeme, Symbol(casted_val, self.get_type(casted_val)))
            return True
        
        # Another form of typecast statement
        if isinstance(statement, RecastStatement):
            if FUNC_mode:
                if not sym_table.indentifier_exists(statement.varident.lexeme):
                    self.printError(Errors.UNDEFINED_VAR_FUNC, statement.varident, funcident)
                    return None
            else:
                if not self.sym_table.indentifier_exists(statement.varident.lexeme):
                    self.printError(Errors.REFERENCED_UNDEFINED_VAR, statement.varident)
                    return None
                
            val = None

            if FUNC_mode:
                val = sym_table.retrieve_val(statement.varident.lexeme)
            else:
                val = self.sym_table.retrieve_val(statement.varident.lexeme)

            casted_val = self.cast_literal_value(val.value, statement.type.token_type)

            if casted_val == None:
                self.printError(Errors.CANT_TYPECAST_VAR, statement.varident, statement.type)
                return None
            
            if FUNC_mode:
                sym_table.modify_symbol(statement.varident.lexeme, Symbol(casted_val, self.get_type(casted_val)))
                return True
            
            self.sym_table.modify_symbol(statement.varident.lexeme, Symbol(casted_val, self.get_type(casted_val)))
            return True
        
        # Loop
        if isinstance(statement, LoopStatement):
            loop_ident = statement.loopident

            # check first if counter variable is declared
            if FUNC_mode:
                if not sym_table.indentifier_exists(statement.counter.lexeme):
                    self.printError(Errors.REFERENCED_UNDEFINED_VAR, statement.counter)
                    return None
            else:
                if not self.sym_table.indentifier_exists(statement.counter.lexeme):
                    self.printError(Errors.REFERENCED_UNDEFINED_VAR, statement.counter)
                    return None
            
            cond = statement.loop_cond.comparison
            
            while True:
                cond_result = None

                # Cast first the value of counter to num
                casted_val = None

                if FUNC_mode:
                    casted_val = sym_table.retrieve_val(statement.counter.lexeme)
                else:
                    casted_val = self.sym_table.retrieve_val(statement.counter.lexeme)

                if casted_val == None:
                    self.printError(Errors.REFERENCED_UNDEFINED_VAR, casted_val)
                    return None
                
                if casted_val.type not in (TokenType.NUMBAR_TYPE, TokenType.NUMBR_TYPE):
                    casted_val = self.literal_to_num(casted_val.value)

                    if casted_val == None:
                        self.printError(Errors.INVALID_LOOP_COUNTER, statement.counter, loop_ident)
                        return None
                    
                    # Successfully casted num into an integer, modify now the sym_table

                    if FUNC_mode:
                        sym_table.modify_symbol(statement.counter.lexeme, Symbol(casted_val, self.get_type(casted_val)))
                    else:
                        self.sym_table.modify_symbol(statement.counter.lexeme, Symbol(casted_val, self.get_type(casted_val)))

                # check first if the condition is true
                if isinstance(statement.loop_cond.expression, Expression):
                    cond_result = self.evaluate_expression(statement.loop_cond.expression, FUNC_mode, sym_table)

                    if cond_result == None:
                        return None
                    
                    cond_result = self.literal_to_bool(cond_result)
                elif isinstance(statement.loop_cond.expression, TokenClass):
                    cond_result = self.unwrap_bool(statement.loop_cond.expression)

                    if cond_result == None:
                        return None
                
                # Condition check
                if cond.token_type == TokenType.TIL:
                    if cond_result == True:
                        break
                elif cond.token_type == TokenType.WILE:
                    if cond_result == False:
                        break
                    
                # If it reached here, it means that statements must be executed
                for s in statement.statements:
                    if isinstance(s, Terminator):
                        break
                    
                    if self.execute_statement(s, FUNC_mode, sym_table, funcident, parent_sym_table):
                        continue
                    else:
                        return None
                    
                # Now modify the counter
                if statement.step.token_type == TokenType.UPPIN:
                    if FUNC_mode:
                        val = sym_table.retrieve_val(statement.counter.lexeme)
                        sym_table.modify_symbol(statement.counter.lexeme, Symbol(val.value + 1, val.type))
                    else:
                        val = self.sym_table.retrieve_val(statement.counter.lexeme)
                        self.sym_table.modify_symbol(statement.counter.lexeme, Symbol(val.value + 1, val.type))
                elif statement.step.token_type == TokenType.NERFIN:
                    if FUNC_mode:
                        val = sym_table.retrieve_val(statement.counter.lexeme)
                        sym_table.modify_symbol(statement.counter.lexeme, Symbol(val.value - 1, val.type))
                    else:
                        val = self.sym_table.retrieve_val(statement.counter.lexeme)
                        self.sym_table.modify_symbol(statement.counter.lexeme, Symbol(val.value - 1, val.type))

            # Delimiter identifier must match the loop identifier at top
            if statement.delim_loop_ident.lexeme != loop_ident.lexeme:
                self.printError(Errors.LOOP_IDENT_MISMATCH, statement.delim_loop_ident, loop_ident)
                return None
            
            return True
                    
                