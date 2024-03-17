
from compiler.models.expressions import *
from compiler.models.types import *
from compiler.models.symbol_table import *

# TODO: own exception types
# TODO: table to track types of variables
# TODO: add a Type to each AST node
def typecheck(exp: Expression, variables: SymTab = SymTab({})) -> Type:
    if isinstance(exp, Module):
        node = exp.sequence[0]
        # first collect all functions for recursive calls
        for i in range(1, len(exp.sequence)):
            fun = exp.sequence[i]
            if isinstance(fun, FunctionDeclaration):
                variables.variables[fun.name] = fun.type
        # then check them
        for i in range(1, len(exp.sequence)):
            fun = exp.sequence[i]
            if isinstance(fun, FunctionDeclaration):
                temp = variables
                for arg in fun.args:
                    temp.variables[arg.get_name()] = arg.type
                check_type(fun, variables)
    else:
        node = exp

    node.type = check_type(node, variables)
    return node.type

def check_type(node: Expression, variables: SymTab = SymTab({})) -> Type:
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
            match node.name:
                case 'print_int':
                    if len(node.args) == 1:
                        t1 = typecheck(node.args[0], variables)
                        if t1 is not Int:
                            raise Exception(f"Function {node.name} argument was {t1}")
                        return Unit
                    raise Exception(f'Unsupported arguments for the print_int function, {node.args}')
                case 'print_bool':
                    if len(node.args) == 1:
                        t1 = typecheck(node.args[0], variables)
                        if t1 is not Bool:
                            raise Exception(f"Function {node.name} argument was {t1}")
                        return Unit
                    raise Exception(f'Unsupported arguments for the print_bool function, {node.args}')
                case 'read_int':
                    if len(node.args) != 0:
                        raise Exception(f'Function {node.name} expects 0 parameters, got {len(node.args)}')
                    return Int
                case _:
                    root_sym = variables
                    while isinstance(root_sym, HierarchicalSymTab):
                        root_sym = root_sym.parent
                    if node.name in root_sym.variables:
                        return root_sym.variables[node.name]
                    else:
                        raise Exception(f'Undeclared function {node.name}')
                        
        case Block():
            for i in range(0, len(node.sequence)-1):
                typecheck(node.sequence[i], variables)
            return typecheck(node.sequence[len(node.sequence)-1], variables)
        
        case FunctionDeclaration():
            body_type = typecheck(node.body, variables)
            if body_type != node.type:
                raise Exception(f'Function {node.name} expects to return type {node.type}, but returned {body_type}')
            return body_type
        
        case ReturnExpression():
            return typecheck(node.value)
        
        case _:
            raise Exception(f'Unsupported AST node: {node}')
        