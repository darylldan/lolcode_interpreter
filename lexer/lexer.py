from token_type import TokenType
from token_class import TokenClass
import token_classification as tc
import sys
import re

'''
To-Do:
    - Better error messages
'''


class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.line = 1
        self.buffer = ""
        self.token_list: list[TokenClass] = []
        self.reserved_keywords = [
            'I', 'HAS', 'A', 'SUM', 'OF', 'DIFF', 'PRODUKT', 'QUOSHUNT', 'MOD', 'BOTH', 
            'EITHER', 'WON', 'NOT', 'ANY', 'ALL', 'SAEM', 'DIFFRINT', 'BIGGR', 'SMALLR', 
            'IS', 'NOW', 'O', 'RLY?', 'YA', 'RLY', 'NO', 'WAI', 'IM', 'IN', 'YR', 'OUTTA', 
            'HOW', 'IZ', 'IF', 'U', 'SAY', 'SO', 'FOUND'
        ]



        self.generate_lexemes()

    def consume(self):
        self.buffer += self.code[0]
        self.code = self.code[1:]

    def skip(self):
        self.code = self.code[1:]

    def peek(self) -> str:
        return self.code[0]

    def peek_buffer(self) -> str:
        return self.buffer[-1]

    def clear_buffer(self):
        self.buffer = ""

    def match_lexeme(self, buffer: str, line: int) -> TokenClass:
        # print(f"matching:{buffer}")
        for token_type in TokenType:
            # print(token_type)
            matched = re.match(token_type.value, buffer)
            # There is an error here
            # print(matched)
            if matched:
                if ' ' not in buffer:
                    splitted_buffer = buffer.split(" ")
                    if any(item in self.reserved_keywords for item in splitted_buffer):
                        return None
                 # france
                # if token_type is numbr, or numbar, or win or fail cast muna to repective data type
                # can be checked using token_type == TokenType.NUMBR
                return TokenClass(token_type, tc.classify(buffer), buffer, None, line) # eto yung case to case basis win = None = True Fail = False

        return None
    
    def get_lexemes(self) -> list[TokenType]:
        return self.token_list
    
    def is_next_code_ws(self) -> bool:
        return self.peek() == " " or self.peek() == "\t" or self.peek() == "\r"
    
    def is_last_buffer_ws(self) -> bool:
        return self.peek_buffer() == " " or self.peek_buffer() == "\t" or self.peek_buffer == "\r"
    
    def generate_lexemes(self):
        while self.code != "":
            # print(f"line{self.line}")
            # print(f"buffer:{self.buffer} (len={len(self.buffer)})")
            # print(f"peek:{self.peek()}")
            # input()
            
            # Ignore leading white spaces
            if len(self.buffer) == 0 and self.is_next_code_ws():
                self.skip()
                continue
            
            # Consume a character from code, and place it to buffer
            self.consume()

            # Check for double space between keywords
            if len(self.buffer) > 1 and self.is_last_buffer_ws() and self.is_next_code_ws():
                print(f"Double whitespace found between two keywords at line {self.line}", file=sys.stderr)
                exit(1)

            # Matched empty line
            if len(self.buffer) == 1 and self.peek_buffer() == "\n":
                self.line += 1
                self.clear_buffer()
                continue
            
            # String matching
            if self.peek_buffer() == '"':
                new_token = TokenClass(TokenType.STRING_DELIMITER, tc.classify(self.peek_buffer()), self.peek_buffer(), None, self.line)
                print(new_token)
                self.token_list.append(new_token)

                self.clear_buffer()
                while True:
                    # Continuously consume characters until another string delimiter is found
                    self.consume()

                    # We dont allow multiline string, but \n is allowed
                    if self.peek_buffer() == "\n":
                        print(f"Unterminated string literal at line {self.line}.", file=sys.stderr)
                        exit(1)

                    if self.peek_buffer() == '"':
                        new_token = TokenClass(TokenType.STRING_DELIMITER, tc.classify(self.peek_buffer()), self.peek_buffer(), None, self.line)
                        self.token_list.append(new_token)
                        
                        new_token = TokenClass(TokenType.YARN, "String Literal", self.buffer, self.buffer, self.line)
                        self.token_list.append(new_token)
                        self.clear_buffer()
                        break
                continue

            if self.code == "":
                break
            
            if not self.is_next_code_ws() and not self.peek() == "\n":
                continue

            matched_token = self.match_lexeme(self.buffer, self.line)

            # Potential uncaught case: unidentified keyword --  ayusin q tom
            if matched_token == None:
                if self.peek() == "\n" and len(self.buffer) > 0:
                    self.consume()
                    self.clear_buffer()
                    print(f"Unidentified keyword at line {self.line}", file=sys.stderr)
                    exit(1)
                    
                continue

            if matched_token.token_type == TokenType.BTW:   # mine mark
                # enter single line comment matching mode
                # skip until newline is found  increment yung self life +=1 and self clear_buffer()
                while self.peek() != "\n":
                    self.skip()
                self.skip()
                self.line += 1
                self.clear_buffer()
                continue


            if matched_token.token_type == TokenType.OBTW:
                # enter single line comment matching mode until TLDR is found
                while self.code != "" and not self.code.startswith("TLDR"): # while not TLDR and not empty string, continue consuming and incrementing line count, and clearing buffer until TLDR is found
                    if self.peek() == "\n":
                        self.line += 1

                    self.skip() # skip until TLDR is found

                self.consume()  # Skipping 'T' 
                self.consume()  # Skipping 'L' 
                self.consume()  # Skipping 'D'
                self.consume()  # Skipping 'R'

                # TLDR should be strictly followed by a newline
                if self.peek() != "\n":
                    print(f"Unexpected character after TLDR at line {self.line}", file=sys.stderr)
                    exit(1)

                self.consume() # Consuming "\n"
                self.line += 1 # increment line count
                self.clear_buffer() # clear buffer
                continue 

            # add matched_token to tokenList
            print(matched_token)
            self.token_list.append(matched_token)
            print(self.token_list)
            self.clear_buffer()
