from typing import Any
from compiler.parser import BinaryOp, Expression, IfExpression, Literal

Value = int | bool | None

# TODO: add variables, loops, tables, etc...
def interpret(node: Expression) -> Value:
    match node:
        case Literal():
            return node.value
        
        case BinaryOp():
            a: Any = interpret(node.left)
            b: Any = interpret(node.right)
            if node.op == '+': # TODO: operators table
                return a + b
            elif node.op == '-':
                return a - b
            elif node.op == '*':
                return a * b
            elif node.op == '/':
                return a // b
            elif node.op == '<':
                return a < b
            elif node.op == '>':
                return a > b
            else:
                raise Exception(f'Unsupported operator "{node.op}"')
            
        case IfExpression():
            if node.else_clause is not None:
                if interpret(node.cond):
                    return interpret(node.then_clause)
                else:
                    return interpret(node.else_clause)
            else:
                if interpret(node.cond):
                    interpret(node.then_clause)
                return None

            
        case _:
            raise Exception(f'Unsupported AST node: {node}')
