from compiler.models.expressions import *
from compiler.models.tokens import Token
from compiler.models.types import *

def parse(tokens: list[Token]) -> Module:
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
    def parse_code() -> Module:
        sequence: list[Expression] = []
        if peek().type == 'end':
            raise Exception('No code to parse')
        while peek().text == 'fun':
            sequence.append(parse_function())
        ret = parse_expressions()
        if pos != len(tokens):
            raise Exception(f'Not all tokens were parsed. Was {len(tokens)}, parsed {pos}')
        main = [many_to_one(ret)]
        return Module(main + sequence)
    
    def parse_expressions() -> list[Expression]:
        ret: list[Expression] = []
        result: Expression = Literal(None)

        while peek().type != 'end' and peek().text != '}':
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
            if peek().text == '{':
                right = parse_block()
            else:
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
        elif peek().text == 'return':
            return parse_return()
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
            variable_type: Type = Unit
            if peek().text == ':':
                consume(':')
                t = consume()
                variable_type = string_to_type(t.text)
            consume('=')
            initializer = parse_expression()

            return VariableDeclaration(name, initializer, type=variable_type)
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
    
    def parse_function() -> FunctionDeclaration:
        consume('fun')
        name = peek().text
        consume(name)
        args: list[Expression] = []
        consume('(')
        while peek().text != ')':
            var_name = consume().text
            consume(':')
            var_type = consume().text
            if peek().text != ')':
                consume(',')
            args.append(Identifier(name=var_name, type=string_to_type(var_type)))
        consume(')')
        return_type = Unit
        if peek().text == ':':
            consume(':')
            return_type = string_to_type(consume().text)
        body = parse_block()
        return FunctionDeclaration(name=name, args=args, body=body, type=return_type)
    
    def parse_return() -> ReturnExpression:
        consume('return')
        exp = parse_expression()
        consume(';')
        return ReturnExpression(value=exp)

    return parse_code()