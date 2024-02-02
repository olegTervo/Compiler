
from dataclasses import dataclass
from compiler.parser import BinaryOp, Expression, IfExpression, Literal

@dataclass(frozen=True)
class Type:
    "Base class for types"

@dataclass(frozen=True)
class BasicType(Type):
    name: str

Int = BasicType('Int')
Bool = BasicType('Bool')
Unit = BasicType('Unit')

# TODO: own exception types
# TODO: table to track types of variables
# TODO: add a Type to each AST node
def typecheck(node: Expression) -> Type:
    match node:
        case Literal():
            if isinstance(node.value, int):
                return Int
            else:
                raise Exception(f"Don't know the type of literal: {node.value}")
            
        case BinaryOp():
            t1 = typecheck(node.left)
            t2 = typecheck(node.right)
            if node.op in ['+', '-', '*', '/']:
                if t1 is not Int or t2 is not Int:
                    raise Exception(f'Operator {node.op} expects two Ints, got {t1} and {t2}')
                return Int
            elif node.op in ['<', '>']:
                if t1 is not Int or t2 is not Int:
                    raise Exception(f'Operator {node.op} expects two Ints, got {t1} and {t2}')
                return Bool
            else:
                raise Exception(f'Unknown operator: {node.op}')
            
        case IfExpression():
            t1 = typecheck(node.cond)
            if t1 is not Bool:
                raise Exception(f"'if' condition was {t1}")
            t2 = typecheck(node.then_clause)
            if node.else_clause is None:
                return Unit
            t3 = typecheck(node.else_clause)
            if t2 != t3:
                raise Exception(f"'then' and 'else' had different types: {t2} and {t3}")
            return t2
            
        case _:
            raise Exception(f'Unsupported AST node: {node}')