from dataclasses import dataclass, fields
from typing import Any
from compiler.models.expressions import *
from compiler.models.symbol_table import *
from compiler.models.types import *

@dataclass(frozen=True)
class IRVar:
    name: str

    def __repr__(self) -> str:
        return self.name

@dataclass(frozen=True)
class Instruction():
    "Base class for instructions"

    def __str__(self) -> str:
        """Returns a string representation similar to
        our IR code examples, e.g. 'LoadIntConst(3, x1)'"""
        def format_value(v: Any) -> str:
            if isinstance(v, list):
                return f'[{", ".join(format_value(e) for e in v)}]'
            else:
                return str(v)
        args = ', '.join(
            format_value(getattr(self, field.name))
            for field in fields(self)
            if field.name != 'location'
        )
        return f'{type(self).__name__}({args})'

@dataclass(frozen=True)
class Call(Instruction):
    fun: IRVar
    args: list[IRVar]
    dest: IRVar

@dataclass(frozen=True)
class LoadIntConst(Instruction):
    value: int
    dest: IRVar

@dataclass(frozen=True)
class LoadBoolConst(Instruction):
    value: bool
    dest: IRVar

@dataclass(frozen=True)
class Copy(Instruction):
    source: IRVar
    dest: IRVar

@dataclass(frozen=True)
class Label(Instruction):
    name: str

@dataclass(frozen=True)
class Jump(Instruction):
    label: Label

@dataclass(frozen=True)
class CondJump(Instruction):
    cond: IRVar
    then_label: Label
    else_label: Label

@dataclass(frozen=True)
class Return(Instruction):
    "return statement"

def generate_ir(root_node: Expression, root_types: dict[IRVar, Type] = {}) -> list[Instruction]:
    
    var_types: dict[IRVar, Type] = root_types.copy()

    # 'var_unit' is used when an expression's type is 'Unit'.
    var_unit = IRVar('unit')
    var_types[var_unit] = Unit
    
    next_var_number = 1
    next_label_number = 1
    instructions: list[Instruction] = []

    def new_var(t: Type) -> IRVar:
        nonlocal next_var_number
        var = IRVar(f'x{next_var_number}')
        next_var_number += 1
        return var
    
    def new_label() -> Label:
        nonlocal next_label_number
        label = Label(f'L{next_label_number}')
        next_label_number += 1
        return label
    
    def visit(node: Expression, variables: SymTab) -> IRVar:
        match node:
            case Literal():
                match node.value:
                    case bool():
                        var = new_var(Bool)
                        instructions.append(LoadBoolConst(node.value, var))
                    case int():
                        var = new_var(Int)
                        instructions.append(LoadIntConst(node.value, var))
                    case None:
                        var = var_unit
                    case _:
                        raise Exception(f"loc(TODO): unsupported literal: {type(node.value)}")
                    
                return var
            
            case Identifier():
                if node.name in variables.variables:
                    return variables.variables[node.name]
                elif isinstance(variables, HierarchicalSymTab):
                    return visit(node, variables.parent)
                else:
                    raise Exception(f'Variable {node.name} is not defined')

            
            case BinaryOp():
                var_left = visit(node.left, variables)
                var_right = visit(node.right, variables)

                if isinstance(node.left, Identifier) and node.op == '=':
                    if isinstance(variables.variables, dict) and node.left.name in variables.variables:
                        instructions.append(Copy(var_right, variables.variables[node.left.name]))
                        return variables.variables[node.left.name]
                    elif isinstance(variables, HierarchicalSymTab):
                        return visit(node, variables.parent)
                    else:
                        raise Exception(f'Asserting unknown variable {node.left.name}')
                
                var_result = new_var(node.type)
                instructions.append(Call(
                    fun=IRVar(node.op),
                    args=[var_left, var_right],
                    dest=var_result
                ))
                return var_result
            
            case UnaryOp():
                variable = visit(node.right, variables)
                var_result = new_var(node.type)
                if node.type == BasicType('Int'):
                    instructions.append(Call(
                        fun=IRVar('unary_-'),
                        args=[variable],
                        dest=var_result
                    ))
                elif node.type == BasicType('Bool'):
                    instructions.append(Call(
                        fun=IRVar('unary_not'),
                        args=[variable],
                        dest=var_result
                    ))
                else:
                    raise Exception(f'Unknown unary operation {node.op} with node type {node.type}')
                return var_result

            case IfExpression():
                if node.else_clause is None:
                    l_then = new_label()
                    l_end = new_label()

                    var_cond = visit(node.cond, variables)
                    instructions.append(CondJump(var_cond, l_then, l_end))

                    instructions.append(l_then)
                    var_result = visit(node.then_clause, variables)

                    instructions.append(l_end)
                    return var_result
                else:
                    l_then = new_label()
                    l_else = new_label()
                    l_end = new_label()

                    var_cond = visit(node.cond, variables)
                    instructions.append(CondJump(var_cond, l_then, l_else))

                    var_result = new_var(None)

                    instructions.append(l_then)
                    var_result_then = visit(node.then_clause, variables)
                    instructions.append(Copy(var_result_then, var_result))
                    instructions.append(Jump(l_end))

                    instructions.append(l_else)
                    var_else_result = visit(node.else_clause, variables)
                    instructions.append(Copy(var_else_result, var_result))

                    instructions.append(l_end)
                    return var_result
                
            case VariableDeclaration():
                last = visit(node.initializer, variables)
                var_result = new_var(node.initializer.type)
                instructions.append(Copy(last, var_result))
                variables.variables[node.name] = var_result
                
                return var_unit

            case Block():
                childVariables = HierarchicalSymTab({}, variables)
                for i in range(0, len(node.sequence)-1):
                    visit(node.sequence[i], childVariables)
                return visit(node.sequence[len(node.sequence)-1], childVariables)
            
            case WhileExpression():
                l_start = new_label()
                l_body = new_label()
                l_end = new_label()

                instructions.append(l_start)
                var_cond = visit(node.cond, variables)
                instructions.append(CondJump(var_cond, l_body, l_end))

                instructions.append(l_body)
                var_result_body = visit(node.body, variables)
                instructions.append(Jump(l_start))

                instructions.append(l_end)
                return var_result_body
            
            case _:
                raise Exception(f'Unsupported AST node: {node}')
            

    root_symtab = SymTab({})
    for v in root_types.keys():
        root_symtab.variables[v.name] = v

    instructions.append(Label('start'))
    var_result = visit(root_node, root_symtab)

    if root_node.type == Int:
        instructions.append(Call(
            IRVar("print_int"),
            [var_result],
            new_var(Unit)
        ))
    elif root_node.type == Bool:
        instructions.append(Call(
            IRVar("print_bool"),
            [var_result],
            new_var(Unit)
        ))

    instructions.append(Return())

    return instructions
