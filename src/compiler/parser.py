from dataclasses import dataclass
from compiler.tokenizer import Token


@dataclass
class Expression:
    "base class"

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class Literal(Expression):
    value: int

@dataclass
class BinaryOp(Expression):
    left: Expression
    op: str
    right: Expression

def parse(tokens: list[Token]) -> Expression:
    pos = 0

    def peek() -> Token:
        if pos < len(tokens):
            return tokens[pos]
        else:
            return Token(type='end', text='')
        
    def consume() -> Token:
        token = peek()
        nonlocal pos
        pos += 1
        return token
    
    def parse_literal() -> Literal:
        token = peek()
        if token.type == 'int_literal':
            consume()
            return Literal(value=int(token.text)) # TODO: error handling
        else:
            raise Exception(f'Expected literal, but found {token.text}') # TODO: row, col
    
    # TODO: left and right other than literal
    def parse_expression() -> Expression:
        left = parse_literal()
        op_token = consume() # TODO: parse_token()
        if op_token.text not in ['+', '-', '*', '/']:
            raise Exception(f'Expected operator, got "{op_token.text}"')
        right = parse_literal()
        return BinaryOp(left, op_token.text, right)
    
    return parse_expression()

