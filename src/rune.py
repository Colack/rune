import sys
import os
import logging
from tokens import tokens, keywords

variables = {}

class Rune:
    def __init__(self, program):
        self.program = program
        self.tokens = []
        self.keywords = []
        self.row = 1
        self.column = 0
        self.lexer()
        self.parser()
        self.interpreter()

    def lexer(self):
        length = len(self.program)
        i = 0
        while i < length:
            char = self.program[i]
            if char == '\n':
                self.row += 1
                self.column = 0
                i += 1
                continue
            elif char in ('"', "'"):
                string = ''
                quote_type = char
                i += 1
                while i < length and self.program[i] != quote_type:
                    string += self.program[i]
                    i += 1
                if i < length and self.program[i] == quote_type:
                    i += 1  # Skip closing quote
                self.tokens.append(('STRING', string))
            elif char in ' \t\r':
                i += 1
                continue
            elif char in tokens.values():
                self.tokens.append(('SYMBOL', char))
                i += 1
            else:
                token = ''
                while i < length and self.program[i] not in ' \t\r\n"\'{}()[],;':
                    token += self.program[i]
                    i += 1
                if token in keywords.values():
                    self.tokens.append(('KEYWORD', token))
                else:
                    if token not in variables:
                        variables[token] = None
                    self.tokens.append(('IDENTIFIER', token))
            self.column += 1

        if not any(t[0] == 'KEYWORD' for t in self.tokens):
            self.error('No keywords found')

        with open('tokens.txt', 'w') as file:
            for token in self.tokens:
                file.write(f'{token}\n')

    def parser(self):
        self.statements = []
        i = 0
        while i < len(self.tokens):
            token_type, token_value = self.tokens[i]
            if token_type == 'KEYWORD':
                if token_value in ('string', 'integer', 'character', 'decimal', 'boolean', 'undefined'):
                    i += 1
                    var_type = token_value
                    token_type, token_value = self.tokens[i]
                    if token_type == 'IDENTIFIER':
                        var_name = token_value
                        i += 1
                        token_type, token_value = self.tokens[i]
                        if token_type == 'SYMBOL' and token_value == '=':
                            i += 1
                            expr, i = self.parse_expression(i)
                            self.statements.append(('DECLARATION', var_type, var_name, expr))
                        else:
                            self.error('Expected "=" after variable name')
                elif token_value in ('if', 'else', 'whiletrue', 'whilefalse', 'while', 'for', 'switch', 'return', 'this', 'super', 'class', 'bridge', 'link'):
                    self.statements.append(('STATEMENT', token_value))
                else:
                    self.error(f'Unexpected keyword {token_value}')
            i += 1

    def parse_expression(self, index):
        expr = []
        while index < len(self.tokens):
            token_type, token_value = self.tokens[index]
            if token_type in ('STRING', 'IDENTIFIER', 'SYMBOL'):
                expr.append((token_type, token_value))
                index += 1
            else:
                break
        return expr, index

    def interpreter(self):
        for statement in self.statements:
            if statement[0] == 'DECLARATION':
                var_type, var_name, expr = statement[1], statement[2], statement[3]
                value = self.evaluate_expression(expr)
                variables[var_name] = value
                print(f'{var_type} {var_name} = {value}')
            elif statement[0] == 'STATEMENT':
                print(f'Executing statement: {statement[1]}')

    def evaluate_expression(self, expr):
        if expr[0][0] == 'STRING':
            return expr[0][1]
        return None

    def error(self, message):
        print(f'Rune Error: {message} at line {self.row} and column {self.column}')
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python3 rune.py <file>')
        sys.exit(1)

    if not os.path.exists(sys.argv[1]):
        print(f'Error: File {sys.argv[1]} not found')
        sys.exit(1)

    with open(sys.argv[1], 'r') as file:
        program = file.read()

    rune = Rune(program)
    print('Rune program executed successfully')
