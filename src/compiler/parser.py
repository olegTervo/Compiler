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

@dataclass
class IfExpression(Expression):
    cond: Expression
    then_clause: Expression
    else_clause: Expression | None

def parse(tokens: list[Token]) -> Expression:
    pos = 0

    def peek() -> Token:
        if pos < len(tokens):
            return tokens[pos]
        else:
            return Token(type='end', text='')
        
    def consume(expected: str | None = None) -> Token:
        token = peek()
        if expected is not None and token.text != expected:
            raise Exception(f'Expected "{expected}", got "{token.text}"')
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
        
    # TODO: reduce copy-paste
    def parse_expression() -> Expression:
        left: Expression = parse_polynomial()
        while peek().text in ['<', '>', '==', '>=', '<=']:
            op_token = consume() # TODO: parse_token()
            right = parse_polynomial()
            left = BinaryOp(left, op_token.text, right)
        return left
    
    def parse_polynomial() -> Expression:
        left: Expression = parse_term()
        while peek().text in ['+', '-']:
            op_token = consume() # TODO: parse_token()
            right = parse_term()
            left = BinaryOp(left, op_token.text, right)
        return left
    
    def parse_term() -> Expression:
        left: Expression = parse_factor()
        while peek().text in ['*', '/']:
            op_token = consume() # TODO: parse_token()
            right = parse_factor()
            left = BinaryOp(left, op_token.text, right)
        return left
    
    def parse_factor() -> Expression:
        if peek().text == '(':
            return parse_parenthesized_expression()
        elif peek().text == 'if':
            return parse_if_expression()
        elif peek().type == 'int_literal':
            return parse_literal()
        else:
            raise Exception(f'Unexpected "{peek().text}"')
        
    def parse_parenthesized_expression() -> Expression:
        consume('(')
        expr = parse_expression()
        consume(')')
        return expr
    
    def parse_if_expression() -> Expression:
        consume('if')
        cond = parse_expression()
        consume('then')
        then_clause = parse_expression()
        if peek().text == 'else':
            consume('else')
            else_clause = parse_expression()
        else:
            else_clause = None
        return IfExpression(cond, then_clause, else_clause)        

    return parse_expression()

