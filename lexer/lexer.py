from lexer.token_type import TokenType
from lexer.token_class import TokenClass
from misc.errors import Errors
import lexer.token_classification as tc
import sys
import re
from misc.terminal import Terminal

def prRed(skk): print("\033[91m {}\033[00m" .format(skk), file=sys.stderr, end="")

def prYellow(skk): print("\033[93m {}\033[00m" .format(skk), file=sys.stderr, end="")

'''
Lexer/Scanner

Breaks down the code into tokens to be bundled and analyzed by the parser.
'''

class Lexer:
    def __init__(self, code: str, terminal: Terminal, debug: bool = False, silent = False):
        self.silent = silent
        self.term = terminal
        self.debug = debug      # used for debugging, enters character per character execution mode
        self.code = code
        self.unmodified_code = code
        self.line = 1
        self.buffer = ""
        self.token_list: list[TokenClass] = []
        
        # Since some tokens contains multiple keywords, this list is necessary to not scan those individual keywords as another keywords or as varidents.
        self.reserved_keywords = [
            'I', 'HAS', 'SUM', 'OF', 'DIFF', 'PRODUKT', 'QUOSHUNT', 'MOD', 'BOTH', 
            'EITHER', 'WON', 'ANY', 'ALL', 'SAEM', 'BIGGR', 'SMALLR', 
            'IS', 'NOW', 'O', 'RLY?', 'YA', 'RLY', 'NO', 'WAI', 'IM', 'IN', 'OUTTA', 
            'HOW', 'IZ', 'IF', 'U', 'SAY', 'SO', 'FOUND'
        ]

        # Scanning
        self.generate_lexemes()

    # Moves the first character of the code into the buffer.
    def consume(self):
        self.buffer += self.code[0]
        self.code = self.code[1:]
    
    # Calls consume until newline, BTW or at the end of code.
    def consume_until_newline(self):
        while True:
            if self.peek() == "\n" or self.code.startswith("BTW") or self.peek() == "":
                return
            
            self.consume()

    # Removes the first character of the code.
    def skip(self):
        self.code = self.code[1:]

    #  Returns the next character to be consumed
    def peek(self) -> str:  
        if self.code == "" :
            return ""
        
        return self.code[0]

    # Returns the recently added character to the buffer.
    def peek_buffer(self) -> str:
        return self.buffer[-1]

    # Empties out the buffer
    def clear_buffer(self):
        self.buffer = ""

    # Matches the buffer against all the tokens defined in TokenType enum.
    # Returns a TokenClass of the matched buffer.
    '''
    If matched token that is part of multi-word tokens, it does not match anything if it does not have a space in the buffer.
    It allows for scanning of multi-word tokens that have similar tokens within them.
    '''
    def match_lexeme(self, buffer: str, line: int) -> TokenClass:
        for token_type in TokenType:
            # Skip the undefined token type
            if token_type == TokenType.UNDEFINED or token_type == TokenType.UNTERM_STR:
                continue
            
            # Matching the buffer to any token
            matched = re.match(token_type.value, buffer)
            if matched:
                
                # For lexemes with multiple keywords
                if ' ' not in buffer:
                    splitted_buffer = buffer.split(" ")
                    if any(item in self.reserved_keywords for item in splitted_buffer):
                        return None

                if token_type == TokenType.NUMBR:  # case for int
                    return TokenClass(token_type, tc.classify(token_type.name), buffer, int(buffer), line)
                elif token_type == TokenType.NUMBAR:  # case for float
                    return TokenClass(token_type, tc.classify(token_type.name), buffer, float(buffer), line)
                elif token_type == TokenType.WIN or token_type == TokenType.FAIL:  # check if troof is win or fail
                    if buffer == "WIN": # case for win
                        return TokenClass(token_type, tc.classify(token_type.name), buffer, buffer, line)
                    else:  # case for fail
                        return TokenClass(token_type, tc.classify(token_type.name), buffer, buffer, line)
                elif token_type == TokenType.VARIDENT:
                    return TokenClass(token_type, tc.classify(token_type.name), buffer, None, line)
                
                return TokenClass(token_type, tc.classify(buffer), buffer, None, line)
                   
        return None
    
    def get_lexemes(self) -> list[TokenType]:
        return self.token_list
    
    # Checks if next character to be consumed is a whitespace.
    '''
    Whitespace definition: ' ' (empty space), '\t' (tab), '\r' (carriage return)
    '''
    def is_next_code_ws(self) -> bool:
        return self.peek() == " " or self.peek() == "\t" or self.peek() == "\r"
    
    # Checks if the recently added character to the buffer is a whitespace.
    def is_last_buffer_ws(self) -> bool:
        return self.peek_buffer() == " " or self.peek_buffer() == "\t" or self.peek_buffer == "\r"
    
    # Returns the line of code, given a line number.
    def get_code_line(self, line: int):
        code = ""
        temp_line = 1
        for c in self.unmodified_code:

            if temp_line == line + 1:
                break

            if c == '\n':
                temp_line += 1
            
            if temp_line == line:
                code += c

        return code[1:]
    
    # Used for error printing in the lexer. Usually silenced unless debugging.
    # It also handles the creation of undefined and unterminated tokens.
    def print_error(self, error: Errors, reference_token: TokenClass = None, context_token: TokenClass=None):
        if not self.silent:
            self.term.print_red("Lexer Error: ")
            match error:
                case Errors.DOUBLE_WHITESPACE:
                    self.term.print(f"Double whitespace found between two keywords on")
                    self.term.print_yellow(f"line {self.line}.\n\n")
                    self.term.print(f"\t{self.line} | {self.get_code_line(self.line)}\n")
                    self.term.print_yellow("Tip: Language specification specifies only a single whitespace separating each keyword (except string literals).\n")
                case Errors.UNTERM_STR:
                    self.term.print(f"Unterminated string literal on")
                    self.term.print_yellow(f"line {self.line}.\n\n")
                    self.term.print(f"\t{self.line} | {self.get_code_line(self.line)}\n")
                    self.term.print_yellow("Tip: Language specification prevents multi-line strings.\n")
                case Errors.UNIDENT_KEYWORD:
                    self.term.print(f"Unidentified keyword on")
                    self.term.print_yellow(f"line {self.line}.\n\n")
                    self.term.print(f"\t{self.line} | {self.get_code_line(self.line)}\n")
                case Errors.UNEXPECTED_CHAR_TLDR:
                    self.term.print(f"Unidentified character after TLDR on")
                    self.term.print_yellow(f"line {self.line}.\n\n")
                    self.term.print(f"\t{self.line} | {self.get_code_line(self.line)}\n")
                    self.term.print_yellow("Tip: Place commands in a newline after TLDR.\n")
                case Errors.UNTERM_MULTILINE_COMMENT:
                    self.term.print(f"Unterminated multiline comment on")
                    self.term.print_yellow(f"line {self.line}.")
                    self.term.print(f" OBTW was found on")
                    self.term.print_yellow(f"line {reference_token.line}.\n\n")
                    self.term.print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}")
                    self.term.print(f"\t.\n\t.\n\t.")
                    self.term.print(f"\t{self.line} | {self.get_code_line(self.line)}\n")

    
        self.consume_until_newline()
        error_token = None

        if error == Errors.UNTERM_STR:
            error_token = TokenClass(TokenType.UNTERM_STR, tc.classify(TokenType.UNTERM_STR.name), self.buffer, self.buffer, self.line, Errors.UNTERM_STR)
        elif error == Errors.UNTERM_MULTILINE_COMMENT:
            error_token = TokenClass(TokenType.UNTERM_STR, tc.classify(TokenType.OBTW.name), self.buffer, self.buffer, self.line, Errors.UNTERM_MULTILINE_COMMENT, reference_token)
        else:
            error_token = TokenClass(TokenType.UNDEFINED, tc.classify(TokenType.UNDEFINED.name), self.buffer, self.buffer, self.line, error=error)
        
        self.term.print(error_token)
        self.token_list.append(error_token)
        self.clear_buffer()
    
    # Main scanning algorithm
    def generate_lexemes(self):
        while True:
            # Enables debug mode, character per character execution
            if self.debug:
                self.__debug()

            if self.code == "":
                break

            # Ignore leading white spaces
            if len(self.buffer) == 0 and self.is_next_code_ws():
                self.skip()
                continue
            
            # Consume a character from code, and place it to buffer
            self.consume()

            # Check for double space between keywords
            if len(self.buffer) >= 1 and self.is_last_buffer_ws() and self.is_next_code_ws():
                self.print_error(Errors.DOUBLE_WHITESPACE)
                continue

            # Matched empty line
            if len(self.buffer) == 1 and self.peek_buffer() == "\n":
                self.line += 1
                self.clear_buffer()
                continue
            
            # String matching
            if self.peek_buffer() == '"':
                new_token = TokenClass(TokenType.STRING_DELIMITER, tc.classify(self.peek_buffer()), self.peek_buffer(), None, self.line)
                print(str(new_token))
                self.token_list.append(new_token)
                self.clear_buffer()

                self.clear_buffer()
                while True:
                    if self.debug:
                        self.__debug()
                    # We dont allow multiline string, but \n is allowed
                    if self.peek() == "\n":
                        self.print_error(Errors.UNTERM_STR)
                        break

                    # Continuously consume characters until another string delimiter is found
                    self.consume()

                    if self.peek_buffer() == '"':
                        self.buffer = self.buffer[:-1]
                        
                        str_token = TokenClass(TokenType.YARN, "String Literal", f'{self.buffer}', self.buffer, self.line)
                        print(str(str_token))
                        self.token_list.append(str_token)

                        new_token = TokenClass(TokenType.STRING_DELIMITER, tc.classify('"'), '"', None, self.line)
                        print(str(new_token))
                        self.token_list.append(new_token)
                        self.clear_buffer()
                        break
                continue
            
            if not self.is_next_code_ws() and self.peek() != "\n" and self.peek() != "" and self.peek() != '"':
                continue

            matched_token = self.match_lexeme(self.buffer, self.line)

            # Unidentified token
            if matched_token == None or self.peek() == '"':
                if self.peek() == "\n" and len(self.buffer) > 0:
                    self.print_error(Errors.UNIDENT_KEYWORD)
                    continue

                if self.peek() == '"':
                    self.print_error(Errors.UNIDENT_KEYWORD)
                    continue
                    
                continue

            if matched_token.token_type == TokenType.BTW: 
                # enter single line comment matching mode
                # skip until newline is found  increment yung self life +=1 and self clear_buffer()
                isEOF: bool = False
                while True:
                    if self.debug:
                        self.__debug()

                    if self.peek() == "\n":
                        break

                    if self.peek() == "":
                        isEOF = True
                        break
                    
                    self.skip()
                
                if isEOF:
                    break

                self.skip()
                self.line += 1
                self.clear_buffer()
                continue

            # Multi-line comment scanning
            if matched_token.token_type == TokenType.OBTW:
                isEOF: bool = False
                # enter single line comment matching mode until TLDR is found
                while not self.code.startswith("TLDR"): # while not TLDR and not empty string, continue consuming and incrementing line count, and clearing buffer until TLDR is found
                    
                    if self.debug:
                        self.__debug()

                    if self.peek() == "":
                        isEOF = True
                        break

                    if self.peek() == "\n":
                        self.line += 1

                    self.skip() # skip until TLDR is found
                
                if isEOF:
                    self.print_error(Errors.UNTERM_MULTILINE_COMMENT, matched_token)
                    break

                self.consume()  # Skipping 'T' 
                self.consume()  # Skipping 'L' 
                self.consume()  # Skipping 'D'
                self.consume()  # Skipping 'R'

                self.clear_buffer()

                # TLDR should be strictly followed by a newline
                if self.peek() != "\n":
                    self.print_error(Errors.UNEXPECTED_CHAR_TLDR)
                    continue

                self.consume() # Consuming "\n"
                self.line += 1 # increment line count
                self.clear_buffer() # clear buffer
                continue 

            # add matched_token to tokenList
            print(str(matched_token))
            self.token_list.append(matched_token)
            self.clear_buffer()


    def __debug(self):
        print(f"line{self.line}")
        print(f"buffer:{self.buffer} (len={len(self.buffer)})")
        print(f"peek:{self.peek()}")
        input()