from parser.program import Program
from semantics.symbol_table import SymbolTable
from parser.expression import Expression
from lexer.token_type import TokenType
from lexer.token_class import TokenClass
from misc.errors import Errors
from semantics.symbol import Symbol
from semantics.noob import Noob
from parser.variable_declaration import VariableDeclaration
from parser.io import PrintStatement, InputStatement
from typing import Any, Optional
import sys
import re

def prRed(skk): print("\033[91m {}\033[00m" .format(skk), file=sys.stderr, end="")

def prYellow(skk): print("\033[93m {}\033[00m" .format(skk), file=sys.stderr, end="")

class SemanticAnalyzer():
    def __init__(self, main_program : Program, code: str) -> None:
        self.main_program = main_program
        self.src = code
        self.silent = False
        self.sym_table = SymbolTable()
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
        self.types = [TokenType.NUMBAR_TYPE, TokenType.NUMBR_TYPE, TokenType.YARN_TYPE, TokenType.TROOF]

        self.execute_program()

    def get_sym_table(self) -> dict:
        return self.sym_table.get_sym_table

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
            prRed("Semantic Error: ")
            match error:
                case Errors.UNEXPECTED_OPERATOR:
                    print(f"Unexpected operator '{reference_token.lexeme}' for '{context_token.lexeme}' operation on")
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: Bsta isng type of expression lng, pag arithmetic arithmetic lng den.\n")
                case Errors.INVALID_LITERAL_FOR_INT:
                    print(f"Invalid literal for integer '{reference_token.literal}' on", file=sys.stderr)
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: Dpat wlang decimal ang string pag iconvert s int.\n")
                case Errors.INVALID_LITERAL_FOR_FLOAT:
                    print(f"Invalid literal for integer '{reference_token.literal}' on", file=sys.stderr)
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: String must contain any non-numerical, non-hyphen, non-period characters.\n")
                case Errors.INVALID_OPERAND:
                    print(f"Invalid operand '{reference_token.literal}' for {context_token.lexeme} operation on", file=sys.stderr)
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: Noobs can only be used in boolean operations, and evaluates to false.\n")
                case Errors.CANT_TYPECAST:
                    print(f"Can't typecast '{reference_token.literal}' for {context_token.lexeme} operation on", file=sys.stderr)
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                case Errors.REFERENCED_UNDEFINED_VAR:
                    print(f"Referenced an undefined variable '{reference_token.lexeme}' on ", file=sys.stderr)
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                case Errors.DIVIDE_BY_ZERO:
                    print(f"Division by zero occured on ", file=sys.stderr)
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)
                    prYellow("Tip: No. You just can't.\n")
                case Errors.UNINITIALIZED_VAR:
                    print(f"Uninitialized variable '{reference_token.lexeme}' was used in an '{context_token.lexeme}' operation on", file=sys.stderr)
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n", file=sys.stderr)

    
    def cast_token_value(self, token: TokenClass, type: TokenType) -> any:
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
                            return "FAIL"
                        
                        return "WIN"
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
                            return "FAIL"
                        
                        return "WIN"
            case TokenType.YARN:
                match type:
                    case TokenType.NUMBR_TYPE:
                        str_rep = token.literal
                        match = re.match(TokenType.NUMBR.value, str_rep)

                        if match is not None:
                            return int(token.literal)
                        
                        self.printError(Errors.INVALID_LITERAL_FOR_INT, token)
                    case TokenType.NUMBAR_TYPE:
                        str_rep = token.literal
                        match = re.match(TokenType.NUMBAR.value, str_rep)

                        if match is not None:
                            return float(token.literal)
                        
                        self.printError(Errors.INVALID_LITERAL_FOR_INT, token)
                        return token.literal
                    case TokenType.YARN_TYPE:
                        return token.literal
                    case TokenType.TROOF_TYPE:
                        if token.literal == "":
                            return "FAIL"
                        
                        return "WIN"
            case TokenType.TROOF:
                match type:
                    case TokenType.NUMBR_TYPE:
                        if token.literal == "WIN":
                            return 1
                        
                        return 0
                    case TokenType.NUMBAR_TYPE:
                        if token.literal == "WIN":
                            return 1.0
                        
                        return 0.0
                    case TokenType.YARN_TYPE:
                        return str(token.literal)
                    case TokenType.TROOF_TYPE:
                        return token.literal

    def unwrap_num(self, op: (TokenClass | int | float), tokens: list[TokenClass]) -> (float | int | None):
        if type(op) == int or type(op) == float:
            return op

        if op.token_type == TokenType.VARIDENT:
            op_val: Symbol = self.sym_table.retrieve_val(op.lexeme)
            if op_val == None:
                self.printError(Errors.REFERENCED_UNDEFINED_VAR, op)
                return None
            
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
                return op_val.value
        
        elif op.token_type not in self.numbers:
            if re.match(TokenType.NUMBR.value, op.lexeme):
                return self.cast_token_value(op, TokenType.NUMBR)
            elif re.match(TokenType.NUMBAR.value, op.lexeme):
                return self.cast_token_value(op, TokenType.NUMBAR)
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
    
    def unwrap_bool(self, op: (TokenClass | bool), tokens: list[TokenClass]) -> (bool | None):
        if type(op) == bool:
            return op
            
        if op.token_type == TokenType.VARIDENT:
            op_val: Symbol = self.sym_table.retrieve_val(op.lexeme)
            if op_val == None:
                self.printError(Errors.REFERENCED_UNDEFINED_VAR, op_val)
                return None
            
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
            if op.token_type == TokenType.WIN:
                return True
            else: return False
        else:
            return None
            
    def execute_nesting_expression(self, expression: Expression) -> Optional[Any]:
        stack: list[TokenClass] = []
        
        tokens: list[TokenClass] = expression.expr
        tokens.reverse()

        expr_type = None
        if tokens[-1].token_type in self.arithmetic_operations:
            expr_type = self.arithmetic_operations
        elif tokens[-1].token_type in self.boolean_operations:
            expr_type = self.boolean_operations
        elif tokens[-1].token_type in self.compasion_operations:
            expr_type = self.compasion_operations

        for t in tokens:
            # print(f"now parsing : {t.lexeme}")
            if t.token_type in self.expression_tokens:
                if t.token_type not in expr_type:
                    self.printError(Errors.UNEXPECTED_OPERATOR, t, tokens[-1])
                    return None
                
                match t.token_type:
                    # Arithmetic Operations
                    case TokenType.SUM_OF:
                        'Subtraction'
                        # Pop from the stack
                        op1: (TokenClass | int | float) = stack.pop()
                        op2: (TokenClass | int | float)  = stack.pop()

                        # Unwrap values as num
                        op1_val = self.unwrap_num(op1, tokens)
                        if op1_val == None:
                            return None
                        
                        op2_val = self.unwrap_num(op2, tokens)
                        if op2_val == None:
                            return None
                        
                        # Let python do the float typecasting
                        result = op1_val + op2_val
                        stack.append(result)
                    
                    case TokenType.DIFF_OF:
                        'Subtraction'
                        # Pop from the stack
                        op1: (TokenClass | int | float) = stack.pop()
                        op2: (TokenClass | int | float)  = stack.pop()

                        # Unwrap values as num
                        op1_val = self.unwrap_num(op1, tokens)
                        if op1_val == None:
                            return None
                        
                        op2_val = self.unwrap_num(op2, tokens)
                        if op2_val == None:
                            return None
                        
                        # Let python do the float typecasting
                        result = op1_val - op2_val
                        stack.append(result)
                    
                    case TokenType.PRODUKT_OF:
                        'Multiplication'
                        # Pop from the stack
                        op1: (TokenClass | int | float) = stack.pop()
                        op2: (TokenClass | int | float)  = stack.pop()

                        # Unwrap values as num
                        op1_val = self.unwrap_num(op1, tokens)
                        if op1_val == None:
                            return None
                        
                        op2_val = self.unwrap_num(op2, tokens)
                        if op2_val == None:
                            return None
                        
                        # Let python do the float typecasting
                        result = op1_val * op2_val
                        stack.append(result)
                    
                    case TokenType.QUOSHUNT_OF:
                        'Division'
                        # Pop from the stack
                        op1: (TokenClass | int | float) = stack.pop()
                        op2: (TokenClass | int | float)  = stack.pop()

                        # Unwrap values as num
                        op1_val = self.unwrap_num(op1, tokens)
                        if op1_val == None:
                            return None
                        
                        op2_val = self.unwrap_num(op2, tokens)
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
                    
                    case TokenType.MOD_OF:
                        'Modulo'
                        # Pop from the stack
                        op1: (TokenClass | int | float) = stack.pop()
                        op2: (TokenClass | int | float)  = stack.pop()

                        # Unwrap values as num
                        op1_val = self.unwrap_num(op1, tokens)
                        if op1_val == None:
                            return None
                        
                        op2_val = self.unwrap_num(op2, tokens)
                        if op2_val == None:
                            return None
                        
                        # Let python do the float typecasting
                        result = op1_val % op2_val
                        stack.append(result)

                    case TokenType.BIGGR_OF:
                        'Max'
                        # Pop from the stack
                        op1: (TokenClass | int | float) = stack.pop()
                        op2: (TokenClass | int | float)  = stack.pop()

                        # Unwrap values as num
                        op1_val = self.unwrap_num(op1, tokens)
                        if op1_val == None:
                            return None
                        
                        op2_val = self.unwrap_num(op2, tokens)
                        if op2_val == None:
                            return None
                        
                        # Let python do the float typecasting
                        result = max(op1_val, op2_val)
                        stack.append(result)

                    case TokenType.SMALLR_OF:
                        'Min'
                        # Pop from the stack
                        op1: (TokenClass | int | float) = stack.pop()
                        op2: (TokenClass | int | float)  = stack.pop()

                        # Unwrap values as num
                        op1_val = self.unwrap_num(op1, tokens)
                        if op1_val == None:
                            return None
                        
                        op2_val = self.unwrap_num(op2, tokens)
                        if op2_val == None:
                            return None
                        
                        # Let python do the float typecasting
                        result = min(op1_val, op2_val)
                        stack.append(result)

                    case TokenType.BOTH_OF:
                        print("im here")
                        'And'
                        op1: (TokenClass | str) = stack.pop()
                        op2: (TokenClass | str)  = stack.pop()

                        op1_val = self.unwrap_bool(op1, tokens)
                        if op1_val == None:
                            return None
                        
                        op2_val = self.unwrap_bool(op2, tokens)
                        if op2_val == None:
                            return None
                        
                        print(stack)
                        
                        print(f"{op1_val} AND {op2_val} = {op1_val and op2_val}")
                                                
                        # Unwrap always return a True or False, so it is safe to do bool operations
                        result = op1_val and op2_val
                        stack.append(result)

                    case TokenType.EITHER_OF:
                        'Or'
                        op1: (TokenClass | str) = stack.pop()
                        op2: (TokenClass | str)  = stack.pop()

                        op1_val = self.unwrap_bool(op1, tokens)
                        
                        if op1_val == None:
                            return None
                        
                        op2_val = self.unwrap_bool(op2, tokens)
                        if op2_val == None:
                            return None
                        
                        # Unwrap always return a True or False, so it is safe to do bool operations
                        result = op1_val or op2_val
                        stack.append(result)

                    case TokenType.WON_OF:
                        'XOR'
                        op1: (TokenClass | str) = stack.pop()
                        op2: (TokenClass | str)  = stack.pop()

                        op1_val = self.unwrap_bool(op1, tokens)
                        if op1_val == None:
                            return None
                        
                        op2_val = self.unwrap_bool(op2, tokens)
                        if op2_val == None:
                            return None
                        
                        # Unwrap always return a True or False, so it is safe to do bool operations
                        result = op1_val ^ op2_val
                        stack.append(result)

                    case TokenType.NOT:
                        '!'
                        op1: (TokenClass | str) = stack.pop()

                        op1_val = self.unwrap_bool(op1, tokens)
                        if op1_val == None:
                            return None
                        
                        result = not op1_val
                        stack.append(result)

                    # Comparison - To Do

                    case TokenType.BOTH_SAEM:
                        '=='

                        op1 = stack.pop()
                        op2 = stack.pop()


            else:              
                stack.append(t)

            # print("stack:")
            # print([str(x) for x in stack])

        return stack[0]
    
    def get_type(self, val: any) -> TokenType:
        if type(val) == bool:
            return TokenType.TROOF
        elif type(val) == int:
            return TokenType.NUMBR
        elif type(val) == float:
            return TokenType.NUMBAR
        elif type(val) == str:
            return TokenType.YARN
            
    def execute_program(self):
        # Variable declaration execution
        variable_declarations: list[VariableDeclaration] = self.main_program.variableList.variable_declarations

        for v in variable_declarations:
            print(f"{v.varident.lexeme} -> {v.value}")

        for v in variable_declarations:
            print(f"now executing: {v.varident.lexeme}")
            if v.itz == None:
                self.sym_table.add_symbol(v.varident.lexeme, Symbol(Noob.NOOB, TokenType.NOOB))
                continue

            # Else, itz must be present so it needs to be evaluated
            val = v.value
            print(isinstance(val, Expression))

            if type(val) == TokenClass:
                print(f"{v.varident.lexeme} is tokenclass")
                print(f"value is {val.literal} and type is {val.token_type}")
                self.sym_table.add_symbol(v.varident.lexeme, Symbol(val.literal, val.token_type))
            elif isinstance(val, Expression):
                print(f"{v.varident.lexeme} is expr")
                expr_type = v.value.expr[0]

                result = self.execute_nesting_expression(v.value)
                print(f"result from executing {v.varident.lexeme}: {result}")

                if result == None:
                    return None

                if type(result) == bool:
                    if result == True:
                        result = "WIN"
                    else:
                        result = "FAIL"
                
                expr_type = self.get_type(result)
                self.sym_table.add_symbol(v.varident.lexeme, Symbol(result, expr_type))
                continue
        
        # Initial symbol table is done, proceed to statement parsing
        self.sym_table.__print_sym__()

        for s in self.main_program.statementList:
            # Visible
            if isinstance(s, PrintStatement):
                output_buffer = ""
                # print(f"args: {[str(x) for x in s.args]}")

                for args in s.args:
                    if isinstance(args, Expression):
                        result = self.execute_nesting_expression(args)

                        if result == None:
                            return
                        
                        output_buffer += str(result)

                    # Could either be varident or literal
                    if type(args) == TokenClass:
                        # A varident
                        if args.token_type == TokenType.VARIDENT:
                            retrieved_val = self.sym_table.retrieve_val(args.lexeme)

                            if retrieved_val == None:
                                self.printError(Errors.REFERENCED_UNDEFINED_VAR, args)
                                return
                            
                            if retrieved_val.value == Noob.NOOB:
                                output_buffer += ""
                                continue
                            
                            output_buffer += str(retrieved_val.value)
                        else:
                            # A literal
                            output_buffer += self.cast_token_value(args, TokenType.YARN_TYPE)

                    
                output_buffer += '\n'
                    
                print(output_buffer.replace('\\n', '\n').replace('\\t', '\t'), end="")
                continue

            if isinstance(s, InputStatement):
                if not self.sym_table.indentifier_exists(s.varident.lexeme):
                    self.printError(Errors.REFERENCED_UNDEFINED_VAR, s.varident)
                    return

                input_buffer = input()

                self.sym_table.modify_symbol(s.varident.lexeme, Symbol(input_buffer, TokenType.YARN))
                continue

            if isinstance(s, Expression):
                result = self.execute_nesting_expression(s)
                if result == None:
                    return
                
                self.sym_table.set_IT(Symbol(result, self.get_type(result)))
                self.sym_table.__print_sym__()
                continue
            






                

