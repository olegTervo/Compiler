from dataclasses import dataclass
from typing import Any, Callable

from compiler.models.expressions import *
from compiler.models.symbol_table import *

Value = Callable | int | bool | None
PredefinedSymbols = {
    '+': lambda x, y: x + y,
    '-': lambda x, y: x - y,
    '*': lambda x, y: x * y,
    '/': lambda x, y: x // y,
    '<': lambda x, y: x < y,
    '>': lambda x, y: x > y,
    '==': lambda x, y: x == y,
    '<=': lambda x, y: x <= y,
    '>=': lambda x, y: x == y,
    '!=': lambda x, y: x == y,
    '%': lambda x, y: x % y,
    'and': lambda x, y, var: and_operation(x, y, var),
    'or': lambda x, y, var: or_operation(x, y, var),

    'unary_negative': lambda x: not x if isinstance(x, bool) else -x,
}

# TODO: add variables, loops, tables, etc...
def interpret(node: Expression, variables: SymTab = SymTab(variables=PredefinedSymbols)) -> Value:
    match node:
        case Literal():
            if isinstance(node.value, bool):
                return node.value == True
            return node.value
        
        case Identifier():
            if node.name in variables.variables:
                return variables.variables[node.name]
            elif isinstance(variables, HierarchicalSymTab):
                return interpret(node, variables.parent)
            else:
                raise Exception(f'Variable {node.name} is not defined')
        
        case BinaryOp():
            if isinstance(node.left, Identifier) and node.op == '=':
                if isinstance(variables.variables, dict) and node.left.name in variables.variables:
                    variables.variables[node.left.name] = interpret(node.right, variables)
                    return None
                elif isinstance(variables, HierarchicalSymTab):
                    return interpret(node, variables.parent)
                else:
                    raise Exception(f'Asserting unknown variable {node.left.name}')

            topVar = variables
            while isinstance(topVar, HierarchicalSymTab):
                topVar = topVar.parent
            if node.op in topVar.variables:
                if node.op in ['or', 'and']:
                    return topVar.variables[node.op](node.left, node.right, variables)
                else:
                    a: Any = interpret(node.left, variables)
                    b: Any = interpret(node.right, variables)
                    return topVar.variables[node.op](a, b)
            else:
                raise Exception(f'Unsupported operator "{node.op}"')
            
        case UnaryOp():
            x: Any = interpret(node.right, variables)
            op = 'unary_negative'
            topVar = variables
            while isinstance(topVar, HierarchicalSymTab):
                topVar = topVar.parent
            if op in topVar.variables:
                return topVar.variables[op](x)
            else:
                raise Exception("Couldn't find unary operator")

            
        case IfExpression():
            if node.else_clause is not None:
                if interpret(node.cond, variables):
                    return interpret(node.then_clause, variables)
                else:
                    return interpret(node.else_clause, variables)
            else:
                if interpret(node.cond, variables):
                    interpret(node.then_clause, variables)
                return None
            
        case VariableDeclaration():
            variables.variables[node.name] = interpret(node.initializer, variables)
            return None

        case Block():
            childVariables = HierarchicalSymTab({}, variables)
            for i in range(0, len(node.sequence)-1):
                interpret(node.sequence[i], childVariables)
            return interpret(node.sequence[len(node.sequence)-1], childVariables)
        
        case WhileExpression():
            while interpret(node.cond, variables) == True:
                interpret(node.body, variables)
            return None
        
        case Function():
            match node.name:
                case 'print_int':
                    if len(node.args) == 1 and isinstance(node.args[0], Literal):
                        print(node.args[0].value)
                        return None
                    raise Exception(f'Unsupported arguments for the print_int function, {node.args}')
                case 'print_bool':
                    if len(node.args) == 1 and isinstance(node.args[0], Literal):
                        print(node.args[0].value)
                        return None
                    raise Exception(f'Unsupported arguments for the print_bool function, {node.args}')
                case 'read_int':
                    val = int(input(""))
                    return val
                case _:
                    raise Exception(f'Unsupported function {node.name}')
        case _:
            raise Exception(f'Unsupported AST node: {node}')
        
def or_operation(a: Expression, b: Expression, variables: SymTab) -> bool:
    if interpret(a, variables) == True:
        return True
    else:
        ret = interpret(b, variables)
        if isinstance(ret, bool):
            return ret
    return False

def and_operation(a: Expression, b: Expression, variables: SymTab) -> bool:
    if interpret(a, variables) == False:
        return False
    else:
        ret = interpret(b, variables)
        if isinstance(ret, bool):
            return ret
    return False