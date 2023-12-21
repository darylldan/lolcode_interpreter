from lexer.token_type import TokenType
from lexer.token_class import TokenClass
from misc.errors import Errors
import lexer.token_classification as tc
import sys
import re

def prRed(skk): print("\033[91m {}\033[00m" .format(skk), file=sys.stderr, end="")

def prYellow(skk): print("\033[93m {}\033[00m" .format(skk), file=sys.stderr, end="")

class Lexer:
    def __init__(self, code: str, debug: bool = False, silent = False):
        self.silent = silent
        self.debug = debug      # used for debugging, enters character per character execution mode
        self.code = code
        self.unmodified_code = code
        self.line = 1
        self.buffer = ""
        self.token_list: list[TokenClass] = []
        self.reserved_keywords = [
            'I', 'HAS', 'A', 'SUM', 'OF', 'DIFF', 'PRODUKT', 'QUOSHUNT', 'MOD', 'BOTH', 
            'EITHER', 'WON', 'ANY', 'ALL', 'SAEM', 'BIGGR', 'SMALLR', 
            'IS', 'NOW', 'O', 'RLY?', 'YA', 'RLY', 'NO', 'WAI', 'IM', 'IN', 'OUTTA', 
            'HOW', 'IZ', 'IF', 'U', 'SAY', 'SO', 'FOUND'
        ]

        self.generate_lexemes()

    def consume(self):
        self.buffer += self.code[0]
        self.code = self.code[1:]
        
    def consume_until_newline(self):
        while True:
            if self.peek() == "\n" or self.code.startswith("BTW") or self.peek() == "":
                return
            
            self.consume()

    def skip(self):
        self.code = self.code[1:]

    def peek(self) -> str:  
        if self.code == "" :
            return ""
        
        return self.code[0]

    def peek_buffer(self) -> str:
        return self.buffer[-1]

    def clear_buffer(self):
        self.buffer = ""

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
                elif token_type == TokenType.TROOF:  # check if troof is win or fail
                    if buffer == "WIN": # case for win
                        return TokenClass(token_type, tc.classify(token_type.name), buffer, True, line)
                    else:  # case for fail
                        return TokenClass(token_type, tc.classify(token_type.name), buffer, False, line)
                elif token_type == TokenType.VARIDENT:
                    return TokenClass(token_type, tc.classify(token_type.name), buffer, None, line)
                
                return TokenClass(token_type, tc.classify(buffer), buffer, None, line)
                   
        return None
    
    def get_lexemes(self) -> list[TokenType]:
        return self.token_list
    
    def is_next_code_ws(self) -> bool:
        return self.peek() == " " or self.peek() == "\t" or self.peek() == "\r"
    
    def is_last_buffer_ws(self) -> bool:
        return self.peek_buffer() == " " or self.peek_buffer() == "\t" or self.peek_buffer == "\r"
    
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
    
    def print_error(self, error: Errors, reference_token: TokenClass = None, context_token: TokenClass=None):
        if not self.silent:
            prRed("Lexer Error: ")
            match error:
                case Errors.DOUBLE_WHITESPACE:
                    print(f"Double whitespace found between two keywords on", file=sys.stderr, end="")
                    prYellow(f"line {self.line}.\n\n")
                    print(f"\t{self.line} | {self.get_code_line(self.line)}\n", file=sys.stderr)
                    prYellow("Tip: Language specification specifies only a single whitespace seperating each keywords (except string literals).\n")
                case Errors.UNTERM_STR:
                    print(f"Unterminated string literal on", file=sys.stderr, end="")
                    prYellow(f"line {self.line}.\n\n")
                    print(f"\t{self.line} | {self.get_code_line(self.line)}\n", file=sys.stderr)
                    prYellow("Tip: Language specification prevents multi-line string.\n")
                case Errors.UNIDENT_KEYWORD:
                    print(f"Unidentified keyword on", file=sys.stderr, end="")
                    prYellow(f"line {self.line}.\n\n")
                    print(f"\t{self.line} | {self.get_code_line(self.line)}\n", file=sys.stderr)
                case Errors.UNEXPECTED_CHAR_TLDR:
                    print(f"Unidentified character after TLDR on", file=sys.stderr, end="")
                    prYellow(f"line {self.line}.\n\n")
                    print(f"\t{self.line} | {self.get_code_line(self.line)}\n", file=sys.stderr)
                    prYellow("Tip: Place commands in a newline after TLDR.\n")
                case Errors.UNTERM_MULTILINE_COMMENT:
                    print(f"Unterminated multiline comment on", file=sys.stderr, end="")
                    prYellow(f"line {self.line}.")
                    print(f" OBTW was found on", end="", file=sys.stderr)
                    prYellow(f"line {reference_token.line}.\n\n")
                    print(f"\t{reference_token.line} | {self.get_code_line(reference_token.line)}", file=sys.stderr)
                    print(f"\t.\n\t.\n\t.", file=sys.stderr)
                    print(f"\t{self.line} | {self.get_code_line(self.line)}\n", file=sys.stderr)

    
        self.consume_until_newline()
        error_token = None

        if error == Errors.UNTERM_STR:
            error_token = TokenClass(TokenType.UNTERM_STR, tc.classify(TokenType.UNTERM_STR.name), self.buffer, self.buffer, self.line, Errors.UNTERM_STR)
        elif error == Errors.UNTERM_MULTILINE_COMMENT:
            error_token = TokenClass(TokenType.UNTERM_STR, tc.classify(TokenType.OBTW.name), self.buffer, self.buffer, self.line, Errors.UNTERM_MULTILINE_COMMENT, reference_token)
        else:
            error_token = TokenClass(TokenType.UNDEFINED, tc.classify(TokenType.UNDEFINED.name), self.buffer, self.buffer, self.line, error=error)
        
        print(error_token)
        self.token_list.append(error_token)
        self.clear_buffer()
    
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
            
            newline = "\n"
            # print(f'''{not self.is_next_code_ws()}, {self.peek() != newline}, {self.peek() != ""}, {self.peek() != '"'}''')
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