from dataclasses import dataclass
from compiler.tokenizer import Token


@dataclass
class Expression:
    "base class"

    def ends_with_block(self) -> bool:
        return False

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class Literal(Expression):
    value: int | bool | None

@dataclass
class BinaryOp(Expression):
    left: Expression
    op: str
    right: Expression

    def ends_with_block(self) -> bool:
        return isinstance(self.right, Block)

@dataclass
class UnaryOp(Expression):
    op: str
    right: Expression

    def ends_with_block(self) -> bool:
        return isinstance(self.right, Block)

@dataclass
class IfExpression(Expression):
    cond: Expression
    then_clause: Expression
    else_clause: Expression | None

    def ends_with_block(self) -> bool:
        return (isinstance(self.then_clause, Block) and self.else_clause is None) or isinstance(self.else_clause, Block)

@dataclass
class Function(Expression):
    name: str
    args: list[Expression]

@dataclass
class Block(Expression):
    sequence: list[Expression]

    def ends_with_block(self) -> bool:
        return True
    
@dataclass
class WhileExpression(Expression):
    cond: Expression
    body: Expression

    def ends_with_block(self) -> bool:
        return isinstance(self.body, Block)
    
@dataclass
class VariableDeclaration(Expression):
    name: str
    initializer: Expression

def parse(tokens: list[Token]) -> Expression:
    pos = 0

    def peek() -> Token:
        if pos < len(tokens):
            return tokens[pos]
        else:
            return Token(type='end', text='')
        
    def consume(expected: str | list[str] | None = None) -> Token:
        token = peek()
        if isinstance(expected, str) and token.text != expected:
            raise Exception(f'Expected "{expected}", got "{token.text}"')
        if isinstance(expected, list) and token.text not in expected:
            comma_separated = ", ".join([f'"{e}"' for e in expected])
            raise Exception(f'Parsing fails: expected one of: {comma_separated}')
        nonlocal pos
        pos += 1
        return token
    
    def many_to_one(exps: list[Expression]) -> Expression:
        if len(exps) == 1:
            return exps[0]
        else:
            return Block(exps)
        
    # TODO: reduce copy-paste
    def parse_code() -> Expression:
        if peek().type == 'end':
            raise Exception('No code to parse')
        ret = parse_expressions()
        if pos != len(tokens):
            raise Exception(f'Not all tokens were parsed. Was {len(tokens)}, parsed {pos}')
        
        return many_to_one(ret)
    
    def parse_expressions() -> list[Expression]:
        ret: list[Expression] = []
        result: Expression = Literal(None)

        while peek().type != 'end' and peek().text != '}':
            if peek().text == '{':
                block = parse_block()
                if peek().text == ';':
                    consume(';')
                    ret.append(block)
                elif peek().type != 'end' and peek().text != '}':
                    ret.append(block)
                else:
                    result = block
                    break
            else:
                if peek().text == 'var':
                    exp = parse_variable_declaration()
                else:
                    exp = parse_expression()
                    
                if peek().type != 'end' and peek().text != '}':
                    if not exp.ends_with_block() or peek().text == ';':
                        consume(';')
                    ret.append(exp)
                else:
                    result = exp
                    break
        
        # TODO: parse empty block
        # if len(ret) != 0: 
        ret.append(result)
        return ret
    
    def parse_block() -> Expression:
        consume('{')
        expressions = parse_expressions()
        block = Block(expressions)
        consume('}')
        return block

    # TODO: not, -, while, var
    def parse_expression() -> Expression:
        if peek().text == '{':
            left = parse_block()
        else:
            left = parse_polynomial()
        
        if peek().text == '=':
            consume('=')
            op = '='
            right = parse_expression()
            return BinaryOp(left, op, right)
        
        while peek().text in ['<', '>', '==', '>=', '<=', '!=', '%']:
            op_token = consume() # TODO: parse_token()
            right = parse_polynomial()
            left = BinaryOp(left, op_token.text, right)
        while peek().text in ['or', 'and']:
            op_token = consume(['or', 'and'])
            right = parse_expression()
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
        elif peek().text == 'while':
            return parse_while_expression()
        elif peek().text in ['not', '-']:
            return parse_unary_expression()
        elif peek().type == 'int_literal':
            return parse_literal()
        elif peek().type == 'identifier':
            return parse_identifier()
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
    
    def parse_while_expression() -> Expression:
        consume('while')
        cond = parse_expression()
        consume('do')
        body = parse_expression()
        if isinstance(body, Block):
            return WhileExpression(cond, body)
        else:
            if peek().text == ';':
                consume(';')
                empty = Literal(None)
                return WhileExpression(cond, Block([body, empty]))
            return WhileExpression(cond, body)
    
    def parse_unary_expression() -> Expression:
        op = peek().text
        consume()
        if peek().text in ['not', '-']:
            right = parse_unary_expression()
        else:
            right = parse_expression()
        return UnaryOp(op, right)
    
    def parse_variable_declaration() -> Expression:
        consume('var')
        if peek().type == 'identifier':
            name = peek().text
            consume(name)
            consume('=')
            initializer = parse_expression()

            return VariableDeclaration(name, initializer)
        else:
            raise Exception(f'Expected variable name, but found {peek().text}')

    def parse_literal() -> Literal:
        token = peek()
        if token.type == 'int_literal':
            consume()
            return Literal(value=int(token.text)) # TODO: error handling
        else:
            raise Exception(f'Expected literal, but found {token.text}') # TODO: row, col
        
    def parse_identifier() -> Literal | Identifier | Function:
        token = peek()
        if token.text == 'true':
            consume()
            return Literal(True)
        if token.text == 'false':
            consume()
            return Literal(False)
        if token.type == 'identifier':
            consume()
            next = peek()
            if next.text == '(':
                consume('(')
                args = parse_function_args()
                consume(')')
                return Function(token.text, args)
            else:
                return Identifier(token.text)
        else:
            raise Exception(f'Expected identifier, but found {token.text}')
            
    def parse_function_args() -> list[Expression]:
        args: list[Expression] = []
        while peek().text != ')':
            args.append(parse_expression())
            if peek().text == ',':
                consume(',')
        return args

    return parse_code()

