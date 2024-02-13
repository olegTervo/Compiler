from dataclasses import dataclass
from typing import Any, Callable

from compiler.parser import BinaryOp, Block, Expression, Identifier, IfExpression, Literal, UnaryOp, VariableDeclaration

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
    '==': lambda x, y: x == y,
    '==': lambda x, y: x == y,
    '%': lambda x, y: x % y,
    'and': lambda x, y: False if not x else x and y,
    'or': lambda x, y: True if x else y,

    'unary_negative': lambda x: not x if isinstance(x, bool) else -x,
}

@dataclass
class SymTab():
    variables: dict

@dataclass
class HierarchicalSymTab(SymTab):
    parent: SymTab

# TODO: add variables, loops, tables, etc...
def interpret(node: Expression, variables: SymTab = SymTab(variables=PredefinedSymbols)) -> Value:
    match node:
        case Literal():
            if isinstance(node.value, bool):
                return node.value == True
            return node.value
        
        case Identifier():
            print(variables.variables)
            if node.name in variables.variables:
                return variables.variables[node.name]
            elif isinstance(variables, HierarchicalSymTab):
                return interpret(node, variables.parent)
            else:
                raise Exception(f'Variable {node.name} is not defined')
        
        case BinaryOp():
            if isinstance(node.left, Identifier) and node.op == '=':
                variables.variables[node.left.name] = interpret(node.right, variables)
                print(variables.variables)
                return None

            a: Any = interpret(node.left, variables)
            b: Any = interpret(node.right, variables)
            topVar = variables
            while isinstance(topVar, HierarchicalSymTab):
                topVar = topVar.parent
            if node.op in topVar.variables:
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
                print(childVariables)
            return interpret(node.sequence[len(node.sequence)-1], childVariables)
            
        case _:
            raise Exception(f'Unsupported AST node: {node}')
        