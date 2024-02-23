
from dataclasses import dataclass
from compiler.parser import BinaryOp, Block, Expression, Function, Identifier, IfExpression, Literal, UnaryOp, VariableDeclaration, WhileExpression

@dataclass(frozen=True)
class Type:
    "Base class for types"

@dataclass(frozen=True)
class BasicType(Type):
    name: str

@dataclass
class SymTab():
    variables: dict

@dataclass
class HierarchicalSymTab(SymTab):
    parent: SymTab

Int = BasicType('Int')
Bool = BasicType('Bool')
Unit = BasicType('Unit')
FunType = BasicType('Function')

# TODO: own exception types
# TODO: table to track types of variables
# TODO: add a Type to each AST node
def typecheck(node: Expression, variables: SymTab = SymTab({})) -> Type:
    match node:
        case Literal():
            if isinstance(node.value, bool):
                return Bool
            elif isinstance(node.value, int):
                return Int
            elif node.value is None:
                return Unit
            else:
                raise Exception(f"Don't know the type of literal: {node.value}")
            
        case Identifier():
            if node.name in variables.variables:
                return variables.variables[node.name]
            elif isinstance(variables, HierarchicalSymTab):
                return typecheck(node, variables.parent)
            else:
                raise Exception(f"Variable {node.name} is not defined")
            
        case BinaryOp():
            if isinstance(node.left, Identifier) and node.op == '=':
                if isinstance(variables.variables, dict) and node.left.name in variables.variables:
                    variables.variables[node.left.name] = typecheck(node.right, variables)
                    return Unit
                elif isinstance(variables, HierarchicalSymTab):
                    return typecheck(node, variables.parent)
                else:
                    raise Exception(f'Asserting unknown variable {node.left.name}')

            t1 = typecheck(node.left, variables)
            t2 = typecheck(node.right, variables)
            if node.op in ['+', '-', '*', '/', '%']:
                if t1 is not Int or t2 is not Int:
                    raise Exception(f'Operator {node.op} expects two Ints, got {t1} and {t2}')
                return Int
            elif node.op in ['<', '>', '>=', '<=']:
                if t1 is not Int or t2 is not Int:
                    raise Exception(f'Operator {node.op} expects two Ints, got {t1} and {t2}')
                return Bool
            elif node.op in ['==', '!=']:
                if t1 is not t2:
                    raise Exception(f'Operator {node.op} expects the same types, got {t1} and {t2}')
                return Bool
            elif node.op in ['and', 'or']:
                if t1 is not Bool or t2 is not Bool:
                    raise Exception(f'Operator {node.op} expects two Booleans, got {t1} and {t2}')
                return Bool
            else:
                raise Exception(f'Unknown operator: {node.op}')
            
        case UnaryOp():
            t1 = typecheck(node.right, variables)
            if node.op == '-':
                if t1 is not Int:
                    raise Exception(f'Operator {node.op} expects Int')
                return Int
            elif node.op == 'not':
                if t1 is not Bool:
                    raise Exception(f'Operator {node.op} expects Bool')
                return Bool
            else:
                raise Exception(f'Unknown unary operator: {node.op}')
            
        case IfExpression():
            t1 = typecheck(node.cond, variables)
            if t1 is not Bool:
                raise Exception(f"'if' condition was {t1}")
            t2 = typecheck(node.then_clause, variables)
            if node.else_clause is None:
                return Unit
            t3 = typecheck(node.else_clause, variables)
            if t2 != t3:
                raise Exception(f"'then' and 'else' had different types: {t2} and {t3}")
            return t2
        
        case VariableDeclaration():
            variables.variables[node.name] = typecheck(node.initializer, variables)
            return Unit
        
        case WhileExpression():
            t1 = typecheck(node.cond, variables)
            if t1 is not Bool:
                raise Exception(f"'while' condition {node.cond} was {t1}")
            retval = node.body
            if isinstance(retval, Block):
                retval = retval.sequence[len(retval.sequence)-1]
            t2 = typecheck(retval, variables)
            if t2 is not Unit:
                raise Exception(f"'while' loop return value was {t2}")
            return Unit
        
        case Function():
            raise Exception("Not implemented")
        
        case Block():
            for i in range(0, len(node.sequence)-1):
                typecheck(node.sequence[i], variables)
            return typecheck(node.sequence[len(node.sequence)-1], variables)
        
        case _:
            raise Exception(f'Unsupported AST node: {node}')