from lexer.token_class import TokenClass
from lexer.token_type import TokenType
from misc.errors import Errors
from parser.program import Program
from parser.variable_list import VariableList
from parser.variable_declaration import VariableDeclaration
from parser.io import PrintStatement
import sys

def prRed(skk): print("\033[91m {}\033[00m" .format(skk), file=sys.stderr, end="")

def prYellow(skk): print("\033[93m {}\033[00m" .format(skk), file=sys.stderr, end="")

class Parser():
    def __init__(self, token_list: list[TokenClass], src: str, silent: bool = False):
        self.src = src
        self.token_list = token_list
        self.silent = silent
        self.expression_tokens = (
            TokenType.BOTH_OF,
            TokenType.EITHER_OF,
            TokenType.WON_OF,
            TokenType.NOT,
            TokenType.ALL_OF,
            TokenType.ANY_OF,
            TokenType.BOTH_SAEM,
            TokenType.DIFFRINT,
            TokenType.SUM_OF,
            TokenType.DIFF_OF,
            TokenType.PRODUKT_OF,
            TokenType.QUOSHUNT_OF,
            TokenType.MOD_OF,
            TokenType.BIGGR_OF,
            TokenType.SMALLR_OF,
            TokenType.SMOOSH,
        )

        self.analyze_syntax()

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

        return code[1:]
    
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
        if token_type in (TokenType.YARN, TokenType.NUMBAR, TokenType.NUMBR, TokenType.TROOF, TokenType.STRING_DELIMITER):
            return True
        
        return False
    
    def is_expression_starter(self, token_type: TokenType) -> bool:
        if token_type in self.expression_tokens:
            return True
        
        return False

    def analyze_syntax(self):
        if (self.check_init_errors()):
            exit(1)

        main_program: Program = Program()

        hai: TokenClass = self.pop()
        if hai.token_type == TokenType.HAI:
            main_program.hai = hai
        else:
            self.printError(Errors.EXPECTED_HAI, hai)
            return
    
        wazzup: TokenClass = self.pop()
        if wazzup.token_type == TokenType.WAZZUP:
            main_program.hai = wazzup
        else:
            self.printError(Errors.EXPECTED_WAZZUP, wazzup)
            return
        
        main_program.variableList = VariableList(wazzup)

        # Variable delcaration checking
        while True:
            if self.peek().token_type == TokenType.BUHBYE:
                main_program.variableList.buhbye = self.pop()
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
                
                main_program.variableList.add_variable_declaration(vari_dec)
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
                'Implement expression parser, e2 na yung may node shits'

            if self.peek().line == cur_line:
                self.printError(Errors.UNEXPECTED_TOKEN)
                return
            
            main_program.variableList.add_variable_declaration(vari_dec)

        # Statement parsing
        while True:
            # Code does not end in BUHBYE
            if self.peek().token_type == None:
                if len(main_program.statementList) == 0:
                    self.printError(Errors.EXPECTED_KTHXBYE, main_program.variableList.buhbye)
                    return

                self.printError(Errors.EXPECTED_BUHBYE, main_program.statementList[-1])
                return

            # BUHBYE encountered, meaning program should end
            if self.peek().token_type == TokenType.KTHXBYE:
                if len(self.token_list) > 1:
                    self.pop()
                    unexpected_token = self.pop()
                    self.printError(Errors.UNEXPECTED_TOKEN, unexpected_token)
                    return

                main_program.variableList.buhbye = self.pop()
                break

            token = self.pop()

            # Isa isahin dito yung lahat ng statements

            '''
            Statements (according sa grammar natin):
                - print France
                - input France
                - expr (feel q need natin ng dedicated expression parser)   Daryll 
                - assignment (Mark)

                
                - flow controls
                    - if else 
                    - switch
                    - function
                - typecast (Mark)
            

                VISIBLE "hello" + SUM OF 3 AN 2 + thing
            '''
             #assignment statements

            if token.token_type == TokenType.VARIDENT:
                if self.peek().token_type != TokenType.R:
                    self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
                    return
                
                r = self.pop()
                if self.peek().token_type != TokenType.IS_NOW_A:
                    self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
                    return
                
                is_now_a = self.pop()
                if self.peek().token_type != TokenType.YARN and self.peek().token_type != TokenType.NUMBR and self.peek().token_type != TokenType.NUMBAR and self.peek().token_type != TokenType.TROOF:
                    self.printError(Errors.UNEXPECTED_TOKEN, self.peek())
                    return
                
                value = self.pop()
                if value.token_type == TokenType.YARN or value.token_type == TokenType.NUMBR or value.token_type == TokenType.NUMBAR or value.token_type == TokenType.TROOF:
                    main_program.statementList.append(PrintStatement(token, r, is_now_a, value))
                    
                else:
                    self.printError(Errors.UNEXPECTED_TOKEN, value)
                    return
                
                continue
            


            
        
        



            
            
            


