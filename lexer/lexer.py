from token_type import TokenType
from token_class import TokenClass
import token_classification as tc
import sys
import re


class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.line = 1
        self.buffer = ""
        self.token_list: list[TokenClass] = []

        self.generate_lexemes()

    def consume(self):
        self.buffer += self.code[0]
        self.code = self.code[1:]

    def skip(self):
        self.code = self.code[1:]

    def peak(self) -> str:
        return self.code[0]

    def peak_buffer(self) -> str:
        return self.buffer[-1]

    def clear_buffer(self):
        self.buffer = ""

    def match_lexeme(self, buffer: str, line: int) -> TokenClass:
        for token_type in TokenType:
            matched = re.match(token_type.value)
            if matched: # france
                # if token_type is numbr, or numbar, or win or fail cast muna to repective data type
                # can be checked using token_type == TokenType.NUMBR
                return TokenClass(token_type, tc.classify(buffer), buffer, None, line) # eto yung case to case basis win = None = True Fail = False

        return None

    def generate_lexemes(self):
        while self.code != "":
            self.consume()

            if self.peak() == "\n" and len(self.buffer) > 0:
                self.consume()
                self.clear_buffer()
                print(f"Unidentified keyword", file=sys.stderr)
                continue

            # Matched empty line
            if len(self.buffer) == 1 and self.buffer[0] == "\n":
                self.line += 1
                self.clear_buffer()
                continue
            
            # Daryll
            # String matching
            if self.peak_buffer() == '"':
                # enter string matching mode
                # accept anything until another " is fund
                # append " token to token list
                # Needs error handling,
                continue

            matched_token = self.match_lexeme(self.buffer, self.line)

            if matched_token.token_type == TokenType.BTW:  # mine mark

                # enter single line comment matching mode
                # skip until newline is found, increment yung self life +=1 and self clear_buffer()
                continue

            if matched_token.token_type == TokenType.OBTW:  # mine mark
                # enter single line comment matching mode
                # skip until TLDR is found
                continue

            # add matched_token to tokenList
            self.token_list.append(matched_token)
