from lexer.token_class import TokenClass
from lexer.token_type import TokenType
from misc.errors import Errors
from parser.program import Program
from parser.variable_list import VariableList
from parser.variable_declaration import VariableDeclaration
from parser.io import InputStatement, PrintStatement
from parser.expression import *
from parser.assignment import AssignmentStatement, ImplicitITAssignment
from parser.typecast import TypecastStatement, RecastStatement
from parser.flow_control import IfElseStatement, SwitchCaseStatement, SwitchCaseCase, SwitchCaseDefault, LoopStatement, LoopCondition, Terminator 
from parser.functions import FunctionStatement, FunctionCallStatement, FunctionReturn
import sys, copy
from misc.terminal import Terminal

'''
The parser requires the list of tokens scanned by the lexer.

Bundling of tokens into statement occurs here. The parser produces the Program() object which is then passed on to semantic analyzer for execution.
'''

# Used in printing error statements. Will be replaced by the methods of soon-to-be implemented terminal class.

class Parser():
    def __init__(self, token_list: list[TokenClass], src: str, terminal: Terminal, silent: bool = False):
        self.src = src
        self.term = terminal
        self.token_list = token_list
        self.silent = silent    # Flag to silence the errors
        self.main_program = None
        self.successful_parsing = False

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
        self.types = [TokenType.NUMBAR_TYPE, TokenType.NUMBR_TYPE, TokenType.YARN_TYPE, TokenType.TROOF_TYPE]

        # Used to change the TokenType of a TokenClass into another.
        # Had to keep track of this since this is still used in wait i think this is unnecessary
        self.token_list_orig= copy.deepcopy(self.token_list)
        self.global_counter = 0

        # Proceed into analyzing the main syntax
        self.analyze_syntax()
    
    def get_program(self) -> Program:
        return self.main_program
    
    def get_token_list(self) -> list[TokenClass]:
        return self.token_list_orig
    
    # Only used in updating varidents into loopident or funcident
    def update_token_list(self, type: TokenType, index:int = None) -> None:
        if index == None:
            index = self.global_counter

        self.token_list_orig[index].token_type = type
    
    # Returns None if token_list is empty
    def pop(self) -> (TokenClass | None):
        if len(self.token_list) == 0:
            return None
        
        self.global_counter += 1

        print(f"popped: {self.token_list[0].lexeme}")
        return self.token_list.pop(0)
    
    # Returns the next token to be popped
    def peek(self) -> (TokenClass | None):
        if len(self.token_list) == 0:
            return None
        
        return self.token_list[0]
    
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
    This is called everytime an unexpected token is encountered within the program. It has two parameters:
        - reference_token -> the offending token, passed to this function so that its line of code could be printed and its lexeme could also be used in error messagers.
        - context_token -> optional, used when the error requires at least another token to give context to the error. This is used to provide better error messages.
            - For example:
                - Unterminated loops requires two tokens when printing an error, the offending token (or reference_token) which ius the last line to be parserd (in unterminated stuff, it is usually KTHXBYE) and another token that contains the line where the loop is declared 
    '''
    def printError(self, error: Errors, reference_token: TokenClass, context_token: TokenClass = None):
        print(f"error: {error}, from: {reference_token.line}, {reference_token.lexeme}, {reference_token.token_type}")
        # Parsing errors could be suppressed by passing True to silent optional parameter in class constructor
        if not self.silent:
            self.term.print_red("Parsing Error: ")
            match error:
                case Errors.DOUBLE_WHITESPACE:
                    self.term.print(f"Double whitespace found between two keywords on")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Language specification specifies only a single whitespace seperating each keywords (except string literals).\n")
                case Errors.UNTERM_STR:
                    self.term.print(f"Unterminated string literal on")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Language specification prevents multi-line string.\n")
                case Errors.UNIDENT_KEYWORD:
                    self.term.print(f"Unidentified keyword '{reference_token.lexeme}' on")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                case Errors.UNEXPECTED_CHAR_TLDR:
                    self.term.print(f"Unidentified character after TLDR on")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Place commands in a newline after TLDR.\n")
                case Errors.UNTERM_MULTILINE_COMMENT:
                    self.term.print(f"Unterminated multiline comment on")
                    self.term.print_yellow(f" line {reference_token.line}.")
                    self.term.print(f" OBTW was found on", end="")
                    self.term.print_yellow(f" line {reference_token.error_context.line}.\n\n")
                    self.term.print(f"\t{reference_token.error_context.line} | {self.get_code_line(reference_token.error_context.line)}")
                    self.term.print(f"\t.\n\t.\n\t.")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Multiline comments are ended by 'TLDR'.\n")
                case Errors.EXPECTED_HAI:
                    self.term.print(f"Expected 'HAI' but found '{reference_token.lexeme}' instead on")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Lolcode programs starts with 'HAI' and ends with 'KTHXBYE'.\n")
                case Errors.EXPECTED_WAZZUP:
                    self.term.print(f"Expected 'WAZZUP' but found '{reference_token.lexeme}' instead on")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Variable declaration section should always be after HAI.\n")
                case Errors.EXPECTED_BUHBYE:
                    self.term.print(f"Expected 'BUHBYE' but found '{reference_token.lexeme}' instead on")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Variable declaration section must be closed with 'BUHBYE'.\n")
                case Errors.EXPECTED_IHASA:
                    self.term.print(f"Unexpected token '{reference_token.lexeme}' found on")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Variable declaration section must be closed with 'BUHBYE'\n      Declare variable using 'I HAS A <varident>'.\n")
                case Errors.EXPECTED_VARIDENT:
                    self.term.print(f"Unexpected token '{reference_token.lexeme}' found on")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Declare variable using 'I HAS A <varident>'.\n")
                case Errors.UNEXPECTED_NEWLINE:
                    self.term.print(f"Unexpected newline at")
                    self.term.print_yellow(f" line {context_token.line}.\n\n")
                    self.term.print(f"\tParsing line:")
                    self.term.print(f"\t{context_token.line} | {self.get_code_line(context_token.line)}\n\n")
                    self.term.print(f"\tNext token found on", end="")
                    self.term.print_yellow(f" line {reference_token.line}.\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n\n")
                    self.term.print_yellow("\nTip: Lolcode commands are separated by a newline. Soft command breaks are not currently supported.\n")
                case Errors.UNEXPECTED_TOKEN:
                    self.term.print(f"Unexpected token '{reference_token.lexeme}' found on")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                case Errors.INVALID_VAR_VALUE:
                    self.term.print(f"Invalid variable value '{reference_token.lexeme}' for '{context_token.lexeme}' on")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Supported variable values are literals, variable identifier (reference), or expression.\n") 
                case Errors.UNEXPECTED_OPERAND:
                    self.term.print(f"Unexpected operand '{reference_token.lexeme}' for {context_token.classification} found on")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Expressions in lolcode are in prefix notation.\n")
                case Errors.INVALID_STRING_CONT_ARG:
                    self.term.print(f"Unexpected argument '{reference_token.lexeme}' for {context_token.lexeme} found on")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Only literals and variables are allowed in string concatenation.\n")
                case Errors.INVALID_ARG_SEPARATOR:
                    self.term.print(f"Unexpected token '{reference_token.lexeme}' for '{context_token.lexeme}' operation on")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Operations with multiple arities are separated by 'AN'.\n")
                case Errors.INCOMPLETE_EXPR:
                    self.term.print(f"Incomplete expression found for '{reference_token.lexeme}' operation on")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                case Errors.UNEXPECTED_OPERATOR:
                    self.term.print(f"Unexpected operator '{reference_token.lexeme}' for '{context_token.lexeme}' operation on")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Bsta isng type of expression lng, pag arithmetic arithmetic lng den.\n")
                case Errors.NESTING_IF:
                    self.term.print(f"Nesting IF statements found on")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Nesting IF statements are not yet supported.\n")
                case Errors.UNTERM_IF:
                    self.term.print(f"Unterminated IF-THEN statement found on")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\tParsing line:")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n\n")
                    self.term.print(f"\tIF-THEN statement clause:")
                    self.term.print(f"\t{context_token.line} | {self.get_code_line(context_token.line)}\n\n")
                    self.term.print_yellow("\nTip: IF-THEN statements are terminated by 'OIC'.\n")
                case Errors.NESTING_SC:
                    self.term.print(f"Nesting switch-case statements found on")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Nesting switch-case statements are not yet supported.\n")
                case Errors.MISSING_CASE:
                    self.term.print(f"Unexpected token '{reference_token.lexeme}' found at line")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Switch-case requires at least one non-default case.\n")
                case Errors.INVALID_CASE_VAL:
                    self.term.print(f"Invalid value '{reference_token.lexeme}' for a case key found at line")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Literals are the only keys allowed for cases.\n")
                case Errors.UNTERM_SC:
                    self.term.print(f"Unterminated switch-case statement found on")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\tParsing line:")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n\n")
                    self.term.print(f"\tSwitch-case statement clause:")
                    self.term.print(f"\t{context_token.line} | {self.get_code_line(context_token.line)}\n\n")
                    self.term.print_yellow("\nTip: Switch-case statements are terminated by 'OIC'.\n")
                case Errors.EMPTY_CASE:
                    self.term.print(f"Empty case found on")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Case fallthrough is not currently supported..\n")
                case Errors.NESTING_LP:
                    self.term.print(f"Nesting loop statements found on")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Nesting loop statements are not yet supported.\n")
                case Errors.INVALID_LOOPIDENT:
                    self.term.print(f"Unexpected token '{reference_token.lexeme}' found at line")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Loop identifiers must follow the same conventions as a variable identifier.\n")
                case Errors.INVALID_STEP:
                    self.term.print(f"Invalid loop step '{reference_token.lexeme}' for loop {context_token.lexeme} found at line")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Loop step can be either UPPIN (increment by 1) or NERFIN (decrement by 1).\n")
                case Errors.INVALID_COUNTER:
                    self.term.print(f"Invalid loop counter '{reference_token.lexeme}' for loop {context_token.lexeme} found at line")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Variables are the only valid loop counters.\n")
                case Errors.INVALID_LOOP_COND:
                    self.term.print(f"Invalid loop condition '{reference_token.lexeme}' for loop {context_token.lexeme} found at line")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Loop conditions follow the format (TIL | WILE) <expr>.\n")
                case Errors.UNTERM_LOOP:
                    self.term.print(f"Unterminated loop statement found on")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\tParsing line:")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n\n")
                    self.term.print(f"\tLoop declaration:")
                    self.term.print(f"\t{context_token.line} | {self.get_code_line(context_token.line)}\n\n")
                    self.term.print_yellow("\nTip: Loop statements are terminated by 'IM OUTTA YR <loop_label>'.\n")
                case Errors.NESTING_MULT_ART:
                    self.term.print(f"Nesting multiple arity operations found at line")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Expression with infinite arities can not be nested.\n")
                case Errors.INVALID_FUNCIDENT:
                    self.term.print(f"Unexpected token '{reference_token.lexeme}' found at line")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Function identifiers must follow the same conventions as a variable identifier.\n")
                case Errors.INVALID_FUNCTION_PARAM:
                    self.term.print(f"Invalid function parameter '{reference_token.lexeme}' for function {context_token.lexeme} found at line")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Variable identifiers are the only allowed function parameters.\n")
                case Errors.UNTERM_FUNC:
                    self.term.print(f"Unterminated function declaration found on")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\tParsing line:")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n\n")
                    self.term.print(f"\tFunction declaration:")
                    self.term.print(f"\t{context_token.line} | {self.get_code_line(context_token.line)}\n\n")
                    self.term.print_yellow("\nTip: Function declarations are terminated by 'IF U SAY SO'.\n")
                case Errors.ONLY_FUNC_DEC_ALLOWED:
                    self.term.print(f"Unexpected token '{reference_token.lexeme}' found at line")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Only function declarations are allowed before 'WAZZUP'.\n")
                case Errors.FUNCTION_OVERLOADING:
                    func = self.main_program.func_table.retrieve_func(reference_token.lexeme)
                    self.term.print(f"Function '{reference_token.lexeme}' from")
                    self.term.print_yellow(f" line {reference_token.line} ")
                    self.term.print(f"is already defined at")
                    self.term.print_yellow(f" line {func.how_iz_i.line} ")
                    self.term.print(f".\n\n")
                    self.term.print(f"\tRedefining function here:")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n\n")
                    self.term.print(f"\tFunction already defined here:")
                    self.term.print(f"\t{func.how_iz_i.line} | {self.get_code_line(func.how_iz_i.line)}\n\n")
                    self.term.print_yellow("\nTip: Function overloading is not currently supported.\n")
                case Errors.NESTING_FUNC:
                    self.term.print(f"Nesting function declarations found at")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Functions can't be defined inside functins.\n")
                case Errors.INVALID_FUNC_DECLARATION:
                    self.term.print(f"Illegal function declaration found at")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Functions can only be declared between the 'HAI' and 'KTHXBYE' sections and must not be inside flow control statements.\n")
                case Errors.RETURN_OUTSIDE_FUNC:
                    self.term.print(f"Return statement used outside a function at ")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Return statement 'FOUND YR' could only be used inside a function declaration.\n")
                case Errors.INVALID_RETVAL:
                    self.term.print(f"Invalid return value '{reference_token.lexeme}' found at")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Valid return values are expression, literal, and variables (must be in the parameter).\n")
                case Errors.INVALID_FUNCTION_CALL:
                    self.term.print(f"Invalid function name '{reference_token.lexeme}' in a function call statement found at")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Use the function identifier to call a function.\n")
                case Errors.INVALID_FUNCTION_ARG:
                    self.term.print(f"Invalid function argument '{reference_token.lexeme}' in a function call statement found at")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Function arguments can be a literal, variable, or an expression.\n")
                case Errors.VISIBLE_SEP_EXPECTED:
                    self.term.print(f"Unexpected '{reference_token.lexeme}' keyword in a visible statement found at")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: Visible arguments are separated by '+'.\n")
                case Errors.UNTERM_MULT_ARITY:
                    self.term.print(f"Unterminated '{reference_token.lexeme}' expression found at")
                    self.term.print_yellow(f" line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}\n")
                    self.term.print_yellow("\nTip: 'ALL OF' and 'ANY OF' operations are terminated by 'MKAY'.\n")

    # Checks for initial errors that the lexer detected (Usually unidentified keyword and unterminated strings and comements)
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
    
    # Checks if the token_type passed into this function is a literal.
    '''
    Note: When using this function, always check after if the token type is a string delimiter as you will not get the actual string on the string delimiter. Strings follow the format [STRING DELIMITER, ACTUAL STRING, STRING DELIMITER]. Also pop the last string delimiter after getting the actual string.
    '''
    def is_literal(self, token_type: TokenType) -> bool:
        if token_type in (TokenType.YARN, TokenType.NUMBAR, TokenType.NUMBR, TokenType.STRING_DELIMITER, TokenType.WIN, TokenType.FAIL, TokenType.NOOB):
            return True
        
        return False
    
    # Checks if the token type passed is an expression token.
    def is_expression_starter(self, token_type: TokenType) -> bool:
        if token_type in self.expression_tokens:
            return True
        
        return False
    
    # Expression parser. This is explained in-depth in the README file in the parser folder.
    def parse_expression(self, main_op: TokenClass, NS_mode = False) -> (Expression | None):
        if NS_mode:
            print("parsing expr on NS mode")

        print(f"headop: {main_op.lexeme}")
        expression = None
        expr_type = None    # Needed to know to avoid nesting of different type of expressions

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
            expr_type = self.compasion_operations + self.arithmetic_operations + self.boolean_operations
        elif main_op.token_type in self.mult_arity_bool:
            match main_op.token_type:
                case TokenType.ANY_OF:
                    expression = AnyOfExpression(main_op)
                case TokenType.ALL_OF:
                    expression = AllOfExpression(main_op)
                case TokenType.SMOOSH:
                    expression = StringConcatenation(main_op)
            
            # Infinite arity operations require different parsing technique
            return self.parse_mult_arity(expression)
        
        
        an_counter = 1
        op_counter = 2

        if main_op.token_type == TokenType.NOT:
            an_counter = 0
            op_counter = 1

        while True:
            print(f"op_c: {op_counter}\nan_c: {an_counter}")
            if NS_mode:
                if self.peek().token_type == TokenType.AN:
                    if self.is_expr_valid(expression.expr):
                        return expression
                    
                if self.peek().token_type == TokenType.MKAY:
                    if self.is_expr_valid(expression.expr):
                        return expression
    
            if self.peek().line != main_op.line or self.peek().token_type == TokenType.VISIBLE_CONCATENATOR:
                if op_counter != 0 or an_counter != 0:
                    self.printError(Errors.INCOMPLETE_EXPR, main_op)
                    return None
                                    
                #check if valid expr na,, else unexpected newline
                if self.is_expr_valid(expression.expr):
                    return expression
                
                
                self.printError(Errors.UNEXPECTED_NEWLINE, self.peek(), main_op)
                return None
            
            token = self.pop()
            
            if token.token_type in self.expression_tokens:
                if token.token_type not in expr_type:
                    self.printError(Errors.UNEXPECTED_OPERATOR, token, main_op)
                    return None
                
                expression.add(token)

                if token.token_type != TokenType.NOT:
                    an_counter += 1
                    op_counter += 1     # op_counter -= 1; op_counter += 2

                continue

            if self.is_literal(token.token_type) or token.token_type in (TokenType.VARIDENT, TokenType.IT):
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

                if an_counter == 0:
                    continue

                an = self.pop()

                if an.token_type != TokenType.AN:
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
            return None
    
    # Checks if the expression is valid, uses the prefix expression technique where it should be operand == operators  + 1
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
    def parse_mult_arity(self, expr: Expression):
        # String concatenations have to be parsed differently
        if isinstance(expr, StringConcatenation):
            while True:
                arg = self.pop()

                # Expressions are a one line statement, so it is needed to check if the popped tokens are in the same line
                if arg.line != expr.smoosh.line:
                    self.printError(Errors.UNEXPECTED_NEWLINE, arg, expr.smoosh)
                    return None
                
                # The valid arguments for string concant are literals and varident
                if not (self.is_literal(arg.token_type) or arg.token_type in (TokenType.VARIDENT, TokenType.IT) or arg.token_type == TokenType.STRING_DELIMITER):
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
                    self.printError(Errors.UNEXPECTED_TOKEN, an)
                    return None

                continue
        elif isinstance(expr, AnyOfExpression) or isinstance(expr, AllOfExpression):
            while True:
                arg = self.pop()
                if arg.line != expr.head.line:
                    self.printError(Errors.UNEXPECTED_NEWLINE, arg, expr.head)
                    return None
                
                if arg.token_type in self.mult_arity_bool:
                    self.printError(Errors.NESTING_MULT_ART, arg)
                    return None
                
                if not (self.is_literal(arg.token_type) or arg.token_type in (TokenType.VARIDENT, TokenType.IT)
                 or arg.token_type in self.boolean_operations):
                    self.printError(Errors.UNEXPECTED_TOKEN, arg)
                    return None
                
                
                if arg.token_type in self.boolean_operations:
                    inside_expr = self.parse_expression(arg,NS_mode=True)

                    if inside_expr == None:
                        return None
                    
                    expr.add_param(inside_expr)

                if self.is_literal(arg.token_type):
                    if arg.token_type == TokenType.STRING_DELIMITER:
                        yarn = self.pop()
                        delim = self.pop()

                        expr.add_param(yarn)
                    else:
                        expr.add_param(arg)
                
                if arg.token_type in (TokenType.VARIDENT, TokenType.IT):
                    expr.add_param(arg)

                if self.peek().token_type == TokenType.AN:
                    an = self.pop()

                    if an.line != expr.head.line:
                        self.printError(Errors.UNEXPECTED_NEWLINE, an, expr.head)
                        return None
                
                    continue
                
                # Anyof and allof are terminated by mkay
                if self.peek().token_type == TokenType.MKAY:
                    mkay = self.pop()

                    if mkay.line != expr.head.line:
                        self.printError(Errors.UNEXPECTED_NEWLINE, an, expr.head)
                        return None
                    
                    return expr
                
                self.printError(Errors.UNTERM_MULT_ARITY, expr.head)
                return None
                
        return None
                
    # Analyzes the series of tokens provided by the lexer
    def analyze_syntax(self):
        # Checks first if the lexer caught any errors. If so, do not proceed with parsing
        if (self.check_init_errors()):
            return None

        # Object representation of the lolcode program.
        self.main_program: Program = Program()

        hai: TokenClass = self.pop()
        if hai.token_type == TokenType.HAI:
            self.main_program.hai = hai
        else:
            self.printError(Errors.EXPECTED_HAI, hai)
            return None
        
        # Function parsing mode, since functions can be declared anywhere within the HAI-KTHXBYE scope except inside WAZZUP-BUHBYE scope and other nested scopes.
        while True:
            # WAZZUP encountered, proceed to variable parsing mode
            if self.peek().token_type == TokenType.WAZZUP:
                break

            if self.peek().token_type == TokenType.KTHXBYE:
                self.printError(Errors.EXPECTED_WAZZUP, self.peek())
                return None
            
            # Only expecting function declaration in this section, not statements
            if self.peek().token_type != TokenType.HOW_IZ_I:
                self.printError(Errors.ONLY_FUNC_DEC_ALLOWED, self.peek())
                return None
            
            func_statement = self.parse_function()

            if func_statement == None:
                return None
            
            # Add function to function table
            if self.main_program.add_func(func_statement):
                print(f"function {func_statement.funcident.lexeme} added")
                continue
            else:
                # Function overloading is not allowed.
                self.printError(Errors.FUNCTION_OVERLOADING, func_statement.funcident)
                return None

        # Variable declaration parsing mode
        wazzup: TokenClass = self.pop()
        if wazzup.token_type == TokenType.WAZZUP:
            self.main_program.hai = wazzup
        else:
            self.printError(Errors.EXPECTED_WAZZUP, wazzup)
            return None
        
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
                return None
            
            vari_dec = VariableDeclaration(i_has_a = i_has_a)

            varident = self.pop()
            if varident.line != cur_line:
                self.printError(Errors.UNEXPECTED_NEWLINE, varident, i_has_a)
                return None
            
            if varident.token_type not in (TokenType.VARIDENT, TokenType.IT):
                self.printError(Errors.EXPECTED_VARIDENT, varident)
                return None
            
            vari_dec.varident = varident

            if self.peek().token_type != TokenType.ITZ:
                if self.peek().line == cur_line:
                    self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
                    return None
                
                self.main_program.variableList.add_variable_declaration(vari_dec)
                continue
                
            # ITZ found, must assign a value to the declaration
            itz = self.pop()
            vari_dec.itz = itz

            init_val = self.pop()
            
            if init_val.line != cur_line:
                self.printError(Errors.UNEXPECTED_NEWLINE, init_val, i_has_a)
                return None

            # Possible initial values for vars are literals, expressions, or another variable reference            
            if not (self.is_literal(init_val.token_type) or self.is_expression_starter(init_val.token_type) or (init_val.token_type in (TokenType.VARIDENT, TokenType.IT))):
                self.printError(Errors.INVALID_VAR_VALUE, init_val, vari_dec.varident)
                return None
            
            if init_val.token_type == TokenType.STRING_DELIMITER:
                yarn = self.pop()

                # In theory, this should never get executed
                if yarn.token_type != TokenType.YARN:
                    self.printError(Errors.UNEXPECTED_TOKEN, yarn)
                    return None
                
                vari_dec.value = yarn
                self.pop()
            elif init_val.token_type in (TokenType.VARIDENT, TokenType.IT) or self.is_literal(init_val.token_type):
                vari_dec.value = init_val
            else: # Must be an expression
                val = self.parse_expression(init_val)

                if val == None:
                    return None
                
                vari_dec.value = val

            if self.peek().line == cur_line:
                self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
                return None
            
            self.main_program.variableList.add_variable_declaration(vari_dec)

        # Statement parsing
        while True:
            # Code does not end in BUHBYE
            if self.peek().token_type == None:
                if len(self.main_program.statementList) == 0:
                    self.printError(Errors.EXPECTED_KTHXBYE, self.main_program.variableList.buhbye)
                    return None

                self.printError(Errors.EXPECTED_BUHBYE, self.main_program.statementList[-1])
                return None

            # KTHXBYE encountered, meaning program should end
            if self.peek().token_type == TokenType.KTHXBYE:
                if len(self.token_list) > 1:
                    self.pop()
                    unexpected_token = self.pop()
                    self.printError(Errors.UNEXPECTED_TOKEN, unexpected_token)
                    return None

                self.main_program.variableList.buhbye = self.pop()
                break
            
            # If it returns none, it means that a parsing error has occured, therefore it will no longer analyze statements
            if self.analyze_statement():
                continue

            return None
        
        self.successful_parsing = True

    '''
    Flags:
        IF_MODE -> Analyzing statements inside an IF-ELSE clause, does not allow nesting if IF-ELSE
        FUNC_mode -> Analyzing statements inside a function dec, does not allow functions to be declared inside func
        SC_MODE -> Analyzing staements inside a switch case, does not allow switch case nesting
        LP_MODE -> Analyzing statements inside a loop, does not allow loop nesting

    However, the flow control statements can be nested only once. Goodluck na lang sa semantics HAHAHAHAAHA

    If any of the flags are enabled, it returns the statement that it parsed. Else, it directly adds statement into main_program.
    If none of the flags are enabled, it returns true if successful parsing, else it would return None.
    '''
    def analyze_statement(self, IF_mode: bool = False, FUNC_mode = False, SC_Mode = False, LP_MODE = False) -> (bool | Statement):
        # Function parsing, can also declare function after BUHBYE
        if self.peek().token_type == TokenType.HOW_IZ_I:
            if FUNC_mode:
                self.printError(Errors.NESTING_FUNC, self.peek())
                return None
            
            if IF_mode or SC_Mode or LP_MODE:
                self.printError(Errors.INVALID_FUNC_DECLARATION, self.peek())
                return None
            
            func_statement = self.parse_function()

            if func_statement == None:
                return None
            
            if self.main_program.add_func(func_statement):
                return True
            else:
                self.printError(Errors.FUNCTION_OVERLOADING, func_statement.funcident)
                return None

        token = self.pop()

        # Debug statements
        if IF_mode:
            print(f"analyzing on if mode")
        if SC_Mode:
            print(f"analyzing on sc mode")
        if LP_MODE:
            print(f"analyzing in loop mode")
        if FUNC_mode:
            print(f"analyzing in func mode")

        print(f"now analyzing {token.lexeme}")

        # Return statement. Only valid when parsing staement for loops, switch-case, or functions
        if token.token_type == TokenType.GTFO:
            if not (LP_MODE or FUNC_mode or SC_Mode):
                self.printError(Errors.UNEXPECTED_TOKEN, token)
                return None
            
            return Terminator(token)
        
        '''
        Valid return values will be:
            - Varident
            - Literal
            - Expression
        '''
        # Should return all the statements here since this will only be executed when in fn parsing mode
        if token.token_type == TokenType.FOUND_YR:
            if not FUNC_mode:
                self.printError(Errors.RETURN_OUTSIDE_FUNC, token)
                return None
            
            # Return value could be expression, literal, or varident

            ret_val = self.pop()

            if ret_val.line != token.line:
                self.printError(Errors.UNEXPECTED_NEWLINE, ret_val, token)
                return None
            
            if not(self.is_literal(ret_val.token_type) or self.is_expression_starter(ret_val.token_type) or ret_val.token_type in (TokenType.VARIDENT, TokenType.IT)):
                self.printError(Errors.INVALID_RETVAL, ret_val)
                return None
            
            if self.is_expression_starter(ret_val.token_type):
                expr = self.parse_expression(ret_val)

                if expr == None:
                    return None
                
                return FunctionReturn(token, expr)
            
            if self.is_literal(ret_val.token_type):
                if ret_val.token_type == TokenType.STRING_DELIMITER:
                    yarn = self.pop()
                    delim = self.pop()

                    return FunctionReturn(token, yarn)
                
                return FunctionReturn(token, ret_val)
            
            if ret_val.token_type in (TokenType.VARIDENT, TokenType.IT):
                return FunctionReturn(token, ret_val)
        
        # Function call statement
        if token.token_type == TokenType.I_IZ:
            func_name = self.pop()

            if func_name.line != token.line:
                self.printError(Errors.UNEXPECTED_NEWLINE, func_name, token)
                return None
            
            if func_name.token_type not in (TokenType.VARIDENT, TokenType.IT):
                self.printError(Errors.INVALID_FUNCTION_CALL, func_name)
                return None

            # Update varident tokentype to func_ident
            func_name.token_type = TokenType.FUNC_IDENT

            func_call = FunctionCallStatement(token, func_name)

            expecting_param: bool = False

            # Parsing arguments
            while True:
                if self.peek().line != token.line and not expecting_param:
                    break

                yr = self.pop()

                if yr.line != token.line:
                    self.printError(Errors.UNEXPECTED_NEWLINE, yr, token)
                    return None
                
                if yr.token_type != TokenType.YR:
                    print("error hgere")
                    self.printError(Errors.UNEXPECTED_TOKEN, yr)
                    return None
                
                arg = self.pop()

                if not (self.is_literal(arg.token_type) or self.is_expression_starter(arg.token_type) or arg.token_type in (TokenType.VARIDENT, TokenType.IT)):
                    self.printError(Errors.INVALID_FUNCTION_ARG, arg)
                    return None
                
                if self.is_expression_starter(arg.token_type):
                    expr = self.parse_expression(arg, NS_mode=True)

                    if expr == None:
                        return None
                    
                    func_call.add_arg(expr)
                
                if self.is_literal(arg.token_type):
                    if arg.token_type == TokenType.STRING_DELIMITER:
                        yarn = self.pop()
                        delim = self.pop()

                        func_call.add_arg(yarn)
                    else:
                        func_call.add_arg(arg)

                if arg.token_type in (TokenType.VARIDENT, TokenType.IT):
                    func_call.add_arg(arg)

                expecting_param = False

                if self.peek().line == token.line:
                    if self.peek().token_type != TokenType.AN:
                        self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
                        return None
                    
                    expecting_param = True
                    an = self.pop()
                    continue
            
            if FUNC_mode or LP_MODE or SC_Mode or IF_mode:
                return func_call
            
            print(f"func_args: {[str(x) for x in func_call.args]}")
            self.main_program.add_statement(func_call)
            return True

        # Expression statement parser
        if self.is_expression_starter(token.token_type):
            expr = self.parse_expression(token)

            if expr == None:
                return None
            
            implicit_it = ImplicitITAssignment(expr)
            
            if IF_mode or FUNC_mode or SC_Mode or LP_MODE:
                return implicit_it
            
            self.main_program.add_statement(implicit_it)
            return True
        
        # Implicit IT assignment for literal
        if self.is_literal(token.token_type):
            if token.token_type == TokenType.STRING_DELIMITER:
                yarn = self.pop()
                delim = self.pop()

                implicit_it = ImplicitITAssignment(yarn)

                if IF_mode or FUNC_mode or SC_Mode or LP_MODE:
                    return 
                
                self.main_program.add_statement(implicit_it)
                return True
            
            implicit_it = ImplicitITAssignment(token)
            
            if IF_mode or FUNC_mode or SC_Mode or LP_MODE:
                return implicit_it
            
            self.main_program.add_statement(implicit_it)
            return True

        '''
        Varident can have two possible grammars:
            - Assignment -> varident R <literal | expr>
            - Typecasting -> varident IS NOW A <type>
        '''
        if token.token_type in (TokenType.VARIDENT, TokenType.IT):
            if self.peek().line != token.line:
                # Must be an implicit it assignment
                implicit_it = ImplicitITAssignment(token)

                if IF_mode or FUNC_mode or SC_Mode or LP_MODE:
                    return implicit_it
            
                self.main_program.add_statement(implicit_it)
                return True
                

            next = self.pop()

            # Assignment Statement
            if next.token_type == TokenType.R:
                if self.peek().token_type == TokenType.MAEK:
                    maek = self.pop()

                    if maek.line != next.line:
                        self.printError(Errors.UNEXPECTED_NEWLINE, maek, next)
                        return None

                    # Parsing typecast statement
                    if self.peek().token_type not in (TokenType.VARIDENT, TokenType.IT):
                        self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
                        return None
                        
                    varident = self.pop()

                    if varident.line != token.line:
                        self.printError(Errors.UNEXPECTED_NEWLINE, varident, token)
                        return None
                    
                    a_mutate = None

                    if self.peek().token_type == TokenType.A:
                        a_mutate = self.pop()

                        if a_mutate.line != token.line:
                            self.printError(Errors.UNEXPECTED_NEWLINE, a_mutate, token)
                            return None

                    if self.peek().token_type not in self.types:
                        self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
                        return None
                        
                    var_type = self.pop()

                    if var_type.line != next.line:
                        self.printError(Errors.UNEXPECTED_NEWLINE, var_type, next)
                        return None

                    if IF_mode or FUNC_mode or SC_Mode or LP_MODE:
                        return AssignmentStatement(next, token, TypecastStatement(maek, varident, var_type, a_mutate))
                    
                    self.main_program.add_statement(AssignmentStatement(next, token, TypecastStatement(token, varident, var_type, a_mutate)))
                    return True

                value_token = self.pop()

                if value_token.line != next.line:
                    self.printError(Errors.UNEXPECTED_NEWLINE, value_token, token)
                    return None
                
                if self.is_expression_starter(value_token.token_type):
                    expression = self.parse_expression(value_token)

                    if IF_mode or FUNC_mode or SC_Mode or LP_MODE:
                        return AssignmentStatement(next, token, expression)

                    self.main_program.add_statement(AssignmentStatement(next, token, expression))
                    return True
                
                if value_token.token_type in (TokenType.VARIDENT, TokenType.IT):
                    if IF_mode or FUNC_mode or SC_Mode or LP_MODE:
                        return AssignmentStatement(next, token, value_token)
                    
                    self.main_program.add_statement(AssignmentStatement(next, token, value_token))
                
                if self.is_literal(value_token.token_type):
                    if value_token.token_type == TokenType.STRING_DELIMITER:
                        yarn = self.pop()
                        delim = self.pop()

                        if IF_mode or FUNC_mode or SC_Mode or LP_MODE:
                            return AssignmentStatement(next, token, yarn)

                        self.main_program.add_statement(AssignmentStatement(next, token, yarn))
                        return True
                

                    if IF_mode or FUNC_mode or SC_Mode or LP_MODE:
                        return AssignmentStatement(next, token, value_token)

                    self.main_program.add_statement(AssignmentStatement(next, token, value_token))
                    return True
                
                self.printError(Errors.UNEXPECTED_TOKEN, value_token)
                return None
            
            # Recasting
            if next.token_type == TokenType.IS_NOW_A:
                vartype_token = self.pop()

                if vartype_token.token_type not in self.types:
                    self.printError(Errors.UNEXPECTED_TOKEN, vartype_token)
                    return None
                
                if IF_mode or FUNC_mode or SC_Mode or LP_MODE:
                    return RecastStatement(token, value_token, vartype_token)
                
                self.main_program.add_statement(RecastStatement(token, next, vartype_token))
                return True
            
            self.printError(Errors.UNEXPECTED_TOKEN, next)
            return None

        # Typecasting
        if token.token_type == TokenType.MAEK:
            if self.peek().token_type not in (TokenType.VARIDENT, TokenType.IT):
                self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
                return None
                
            varident = self.pop()

            if varident.line != token.line:
                self.printError(Errors.UNEXPECTED_NEWLINE, varident, token)
                return None

            a_mutate = None

            if self.peek().token_type == TokenType.A:
                a_mutate = self.pop()

                if a_mutate.line != token.line:
                    self.printError(Errors.UNEXPECTED_NEWLINE, a_mutate, token)
                    return None

            if self.peek().token_type not in self.types:
                self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
                return None
                
            var_type = self.pop()

            if IF_mode or FUNC_mode or SC_Mode or LP_MODE:
                return TypecastStatement(token, varident, var_type, a_mutate)
            
            self.main_program.statementList.append(TypecastStatement(token, varident, var_type, a_mutate))
            return True
        
        '''
        Flow Control

        None will be returned instead if a code errors out here
        '''

        # IF-THEN statement
        '''
        No need to parse if an expression is precedes the if statement, since value lang ng IT ang kelangan
        '''
        if token.token_type == TokenType.O_RLY:
            if IF_mode:
                self.printError(Errors.NESTING_IF, token)
                return None
            
            ya_rly = self.pop()

            if ya_rly.line == token.line:
                self.printError(Errors.UNEXPECTED_TOKEN, ya_rly)
                return None
            
            if ya_rly.token_type != TokenType.YA_RLY:
                self.printError(Errors.UNEXPECTED_TOKEN, ya_rly)
                return None
            
            if_else = IfElseStatement(token, ya_rly)
            
            # Parse statements

            # Parsing true clause
            while True:
                # Else statement is optional, to compensate for lack of nesting of if statements
                if self.peek().token_type == TokenType.NO_WAI or self.peek().token_type == TokenType.OIC:
                    print("done analyzing true statements")
                    break

                if self.peek().token_type == TokenType.KTHXBYE:
                    self.printError(Errors.UNTERM_IF, self.peek(), token)
                    return None

                statement = self.analyze_statement(IF_mode= True, FUNC_mode=FUNC_mode, SC_Mode=SC_Mode, LP_MODE=LP_MODE)

                if statement == None:
                    return None
                
                if_else.add_true(statement)

            separator = self.pop()

            # Parsing the else clause
            if separator.token_type == TokenType.NO_WAI:
                if_else.no_wai = separator
                while True:
                    if self.peek().token_type == TokenType.OIC:
                        print("done analyzing false statements")
                        break

                    if self.peek().token_type == TokenType.KTHXBYE:
                        self.printError(Errors.UNTERM_IF, self.peek(), token)
                        return None

                    statement = self.analyze_statement(IF_mode= True, FUNC_mode=FUNC_mode, SC_Mode=SC_Mode, LP_MODE=LP_MODE)

                    if statement == None:
                        return None
                    
                    if_else.add_false(statement)

                oic = self.pop()

                if oic.token_type == TokenType.OIC:
                    if_else.oic = oic
                    # print(f"true: {[str(x) for x in if_else.true_statements]}\n false: {[str(x) for x in if_else.false_statements]}")

                    if SC_Mode or FUNC_mode or LP_MODE:
                        return if_else

                    self.main_program.add_statement(if_else)
                    return True
            
            elif separator.token_type == TokenType.OIC:
                if_else.oic = separator

                if SC_Mode or FUNC_mode or LP_MODE:
                    return if_else
                
                self.main_program.add_statement(if_else)
                return True
            else:
                self.printError(Errors.UNEXPECTED_TOKEN, separator)
                return None
            
        # Switch-case statement
        if token.token_type == TokenType.WTF:
            if SC_Mode:
                self.printError(Errors.NESTING_SC, token)
                return None
            
            switch_case = SwitchCaseStatement(token)

            # Switch-case requires at least one case
            # Parsing first case
            omg_keyword = self.pop()

            if omg_keyword.token_type != TokenType.OMG:
                self.printError(Errors.MISSING_CASE, omg_keyword)
                return None
            
            val = self.pop()
            
            if val.line != omg_keyword.line:
                self.printError(Errors.UNEXPECTED_NEWLINE, val, omg_keyword)
                return None

            if not self.is_literal(val.token_type):
                self.printError(Errors.INVALID_CASE_VAL, val)
                return None
            
            if val.token_type == TokenType.STRING_DELIMITER:
                val = self.pop()
                str_delim = self.pop()

            s_index = 0     # Used to mark cases, see flow_control.py for explanation
            first_case = SwitchCaseCase(omg_keyword, val, s_index)
            
            # Parsing the succeeding cases
            while True:
                if self.peek().token_type == TokenType.OMG or self.peek().token_type == TokenType.OMGWTF or self.peek().token_type == TokenType.OIC:
                    switch_case.add_case(first_case)
                    break

                if self.peek().token_type == TokenType.KTHXBYE:
                    self.printError(Errors.UNTERM_IF, self.peek(), omg_keyword)
                    return None
                
                statement = self.analyze_statement(IF_mode= IF_mode, FUNC_mode=FUNC_mode, SC_Mode=True, LP_MODE=LP_MODE)

                if statement == None:
                    return None
                
                switch_case.add(statement)
                s_index += 1
                # print(f"--------\nadded statement: {str(statement)}\nstatement_index: {s_index - 1}\nnext ind: {s_index}")
                

            # Parse next cases or end of switch-case
            while True:
                # End of switch case
                if self.peek().token_type == TokenType.OIC:
                    oic = self.pop()
                    switch_case.oic = oic

                    if IF_mode or FUNC_mode or LP_MODE:
                        return switch_case
                    
                    self.main_program.add_statement(switch_case)

                    # print([x.index for x in switch_case.cases])
                    # print(f"defalut index: {switch_case.default_case.index}")
                    # print([str(x) for x in switch_case.statements])
                    return True
                
                # Parse another case
                if self.peek().token_type == TokenType.OMG:
                    # print(f"parsing {self.peek().token_type} with lexeme  {self.peek().lexeme}")
                    omg = self.pop()
                    key = self.pop()

                    if key.line != omg.line:
                        self.printError(Errors.UNEXPECTED_NEWLINE, key, omg)
                        return None
                    
                    if not self.is_literal(key.token_type):
                        self.printError(Errors.INVALID_CASE_VAL, key)
                        return None
                    
                    if key.token_type == TokenType.STRING_DELIMITER:
                        key = self.pop()
                        str_delim = self.pop()
                    
                    sc_case = SwitchCaseCase(omg, key, s_index)

                    while True:
                        if self.peek().token_type == TokenType.OMG or self.peek().token_type == TokenType.OMGWTF or self.peek().token_type == TokenType.OIC:
                            
                            switch_case.add_case(sc_case)
                            break

                        if self.peek().token_type == TokenType.KTHXBYE:
                            self.printError(Errors.UNTERM_IF, self.peek(), omg_keyword)
                            return None
                        
                        statement = self.analyze_statement(IF_mode= IF_mode, FUNC_mode=FUNC_mode, SC_Mode=True, LP_MODE=LP_MODE)

                        if statement == None:
                            return None
                        
                        switch_case.add(statement)
                        s_index += 1
                        # print(f"--------\nadded statement: {str(statement)}\nstatement_index: {s_index - 1}\nnext ind: {s_index}")

                # Parse default case
                elif self.peek().token_type == TokenType.OMGWTF:
                    omg_wtf = self.pop()

                    default_case = SwitchCaseDefault(omg_wtf, s_index)

                    while True:
                        if self.peek().token_type == TokenType.OIC:
                            # Cant allow empty cases
                            if len(switch_case.statements[s_index - 1:]) == 0:
                                self.printError(Errors.EMPTY_CASE, omg_wtf)
                                return None
                            
                            switch_case.default_case = default_case
                            break

                        if self.peek().token_type == TokenType.OMG or self.peek().token_type == TokenType.OMGWTF:
                            self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
                            return None
                        
                        if self.peek().token_type == TokenType.KTHXBYE:
                            self.printError(Errors.UNTERM_IF, self.peek(), omg_keyword)
                            return None
                        
                        statement = self.analyze_statement(IF_mode= IF_mode, FUNC_mode=FUNC_mode, SC_Mode=True, LP_MODE=LP_MODE)

                        if statement == None:
                            return None
                        
                        switch_case.add(statement)
                        s_index += 1
                        # print(f"--------\nadded statement: {str(statement)}\nstatement_index: {s_index - 1}\nnext ind: {s_index}")

                else:
                    self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
                    return None
                
        # Loop parsing
        if token.token_type == TokenType.IM_IN_YR:
            if LP_MODE:
                self.printError(Errors.NESTING_LP, token)
                return None

            loop_statement = LoopStatement(token)

            loop_ident = self.pop()

            if loop_ident.line != token.line:
                self.printError(Errors.UNEXPECTED_NEWLINE, loop_ident, token)
                return None
            
            if loop_ident.token_type not in (TokenType.VARIDENT, TokenType.IT):
                self.printError(Errors.INVALID_LOOPIDENT, loop_ident)
                return None
            
            loop_ident.token_type = TokenType.LOOP_IDENT
            loop_statement.loopident = loop_ident

            step = self.pop()

            if step.line != token.line:
                self.printError(Errors.UNEXPECTED_NEWLINE, step, token)
                return None
            
            if step.token_type not in (TokenType.UPPIN, TokenType.NERFIN):
                self.printError(Errors.INVALID_STEP, step, loop_ident)
                return None
            
            loop_statement.step = step

            yr = self.pop()

            if yr.line != token.line:
                self.printError(Errors.UNEXPECTED_NEWLINE, yr, token)
                return None
            
            if yr.token_type != TokenType.YR:
                self.printError(Errors.UNEXPECTED_TOKEN, yr)
                return None
            
            loop_statement.yr = yr

            counter = self.pop()

            if counter.line != token.line:
                self.printError(Errors.UNEXPECTED_NEWLINE, counter, token)
                return None
            
            if counter.token_type not in (TokenType.VARIDENT, TokenType.IT):
                self.printError(Errors.INVALID_COUNTER, counter, loop_ident)
                return None
            
            loop_statement.counter = counter

            condition = LoopCondition()

            comparison = self.pop()

            if comparison.line != token.line:
                self.printError(Errors.UNEXPECTED_NEWLINE, comparison, token)
                return None
            
            if not (comparison.token_type == TokenType.TIL or comparison.token_type == TokenType.WILE):
                self.printError(Errors.INVALID_LOOP_COND, comparison, loop_ident)
                return None
            
            condition.comparison = comparison

            expr = self.pop()

            if expr.line != token.line:
                self.printError(Errors.UNEXPECTED_NEWLINE, expr, token)
                return None

            if not (self.is_expression_starter(expr.token_type) or expr.token_type in (TokenType.VARIDENT, TokenType.IT) or self.is_literal(expr.token_type)):
                self.printError(Errors.INVALID_LOOP_COND, expr, loop_ident)
                return None

            # Condition is an expression
            if self.is_expression_starter(expr.token_type):
                expression = self.parse_expression(expr)

                if expression == None:
                    return None
                
                condition.expression = expression
            else:
                # Must be varident or literal    
                condition.expression = expr

            loop_statement.loop_cond = condition

            if self.peek().line == token.line:
                self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
                return None
            
            # Parse statements inside loop
            while True:
                if self.peek().token_type == TokenType.IM_OUTTA_YR:
                    delimiter = self.pop()

                    if delimiter.line == self.token_list_orig[self.global_counter - 2].line:
                        self.printError(Errors.UNEXPECTED_TOKEN, delimiter)
                        return None
                    
                    loop_statement.im_outta_yr = delimiter
                    
                    delim_lp_ident = self.pop()

                    if delim_lp_ident.line != delimiter.line:
                        self.printError(Errors.UNEXPECTED_NEWLINE, delim_lp_ident, delimiter)
                        return None
                    
                    if delim_lp_ident.token_type not in (TokenType.VARIDENT, TokenType.IT):
                        self.printError(Errors.INVALID_LOOPIDENT, loop_ident)
                        return None
                    
                    delim_lp_ident.token_type = TokenType.LOOP_IDENT
                    loop_statement.delim_loop_ident = delim_lp_ident

                    if IF_mode or FUNC_mode or SC_Mode:
                        return loop_statement
                    
                    # print([str(x) for x in loop_statement.statements])
                    
                    self.main_program.add_statement(loop_statement)
                    return True

                if self.peek().token_type == TokenType.KTHXBYE:
                    self.printError(Errors.UNTERM_LOOP, self.peek(), token)
                    return None
                
                statement = self.analyze_statement(IF_mode= IF_mode, FUNC_mode=FUNC_mode, SC_Mode=SC_Mode, LP_MODE=True)

                if statement == None:
                    return None
                
                loop_statement.add(statement)
                
        # input statement
        if token.token_type == TokenType.GIMMEH:
            if self.peek().token_type not in (TokenType.VARIDENT, TokenType.IT):
                self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
                return False
            if self.peek().line != token.line:
                self.printError(Errors.UNEXPECTED_NEWLINE, self.peek(), token)
                return False
            varident = self.pop()

            if IF_mode or SC_Mode or FUNC_mode or LP_MODE:
                return InputStatement(token, varident)
            
            self.main_program.add_statement(InputStatement(token, varident))
            return True

        # Print statement
        if token.token_type == TokenType.VISIBLE:
            print_statement = PrintStatement(token)
            while True:
                arg = self.pop()
                print(f"now parsing on visible: {arg.lexeme}")

                if arg.line != token.line:
                    self.printError(Errors.UNEXPECTED_NEWLINE, arg, token)
                    return None
                
                if not (self.is_literal(arg.token_type) or arg.token_type in (TokenType.VARIDENT, TokenType.IT) or self.is_expression_starter(arg.token_type)):
                    self.printError(Errors.UNEXPECTED_TOKEN, arg)
                    return None
                # string (yarn ipopop dito)

                if arg.token_type == TokenType.STRING_DELIMITER:
                    yarn = self.pop()
                    if yarn.token_type != TokenType.YARN:
                        self.printError(Errors.UNEXPECTED_TOKEN, yarn)
                        return None
                    
                    print_statement.args.append(yarn)
                    self.pop()
                    
                elif arg.token_type in (TokenType.VARIDENT, TokenType.IT) or self.is_literal(arg.token_type):
                    print_statement.args.append(arg)
                    
                elif arg.token_type in self.expression_tokens:
                    expr = self.parse_expression(arg)

                    if expr == None:
                        return None
                    
                    print_statement.args.append(expr)
                    
                if self.peek().line != token.line:
                    if IF_mode or SC_Mode or FUNC_mode or LP_MODE:
                        return print_statement
                    
                    self.main_program.add_statement(print_statement)
                    return True
                
                plusSign = self.pop()

                if plusSign.token_type == TokenType.VISIBLE_CONCATENATOR:
                    continue
                else:
                    self.printError(Errors.VISIBLE_SEP_EXPECTED, plusSign)
                    return None

        self.printError(Errors.UNEXPECTED_TOKEN, token)
        return None

    # Function parser
    # Peek first before calling this function, self.peek().token_type == TokenType.HOW_IZ_I  
    def parse_function(self) -> (FunctionStatement | None):
        how_iz_i = self.pop()

        func_statement = FunctionStatement(how_iz_i)

        func_ident = self.pop()

        if func_ident.line != how_iz_i.line:
            self.printError(Errors.UNEXPECTED_NEWLINE, func_ident, how_iz_i)
            return None
        
        if func_ident.token_type not in (TokenType.VARIDENT, TokenType.IT):
            self.printError(Errors.INVALID_FUNCIDENT, func_ident)
            return None
        
        func_statement.funcident = func_ident

        expecting_param: bool = False

        # Parse parameters
        while True:
            if self.peek().line != how_iz_i.line and not expecting_param:
                break

            yr = self.pop()

            if yr.line != how_iz_i.line:
                self.printError(Errors.UNEXPECTED_NEWLINE, yr, how_iz_i)
                return None
            
            if yr.token_type != TokenType.YR:
                self.printError(Errors.UNEXPECTED_TOKEN, yr)
                return None
            
            # Now expecting a varident

            param = self.pop()

            if param.line != how_iz_i.line:
                self.printError(Errors.UNEXPECTED_NEWLINE, param, how_iz_i)
                return None
            
            if param.token_type not in (TokenType.VARIDENT, TokenType.IT):
                self.printError(Errors.INVALID_FUNCTION_PARAM, param, func_ident)
                return None
            
            func_statement.add_param(param)
            expecting_param = False

            # if true, expecting another parameter
            if self.peek().line == how_iz_i.line:
                if self.peek().token_type != TokenType.AN:
                    self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
                    return None
                
                expecting_param = True
                an = self.pop()
                continue

        # now parse the statements
        while True:
            if self.peek().token_type == TokenType.IF_U_SAY_SO:
                if self.peek().line == self.token_list_orig[self.global_counter - 2]:
                    self.printError(Errors.UNEXPECTED_TOKEN)
                    return None
                
                break

            if self.peek() == TokenType.KTHXBYE:
                self.printError(Errors.UNTERM_FUNC, self.peek(), how_iz_i)
                return None

            statement = self.analyze_statement(FUNC_mode=True)

            if statement == None:
                return None
            
            func_statement.add_statement(statement)

        if_u_say_so = self.pop()

        func_statement.if_u_say_so = if_u_say_so

        return func_statement