from dataclasses import dataclass
from compiler.parser import BinaryOp, Expression, IfExpression, Literal

@dataclass(frozen=True)
class IRVar:
    name: str

    def __repr__(self) -> str:
        return self.name

@dataclass(frozen=True)
class Instruction():
    "Base class for instructions"

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

def generate_ir(root_node: Expression) -> list[Instruction]:
    next_var_number = 1
    next_label_number = 1
    instructions = []

    def new_var() -> IRVar:
        nonlocal next_var_number
        var = IRVar(f'x{next_var_number}')
        next_var_number += 1
        return var
    
    def new_label() -> Label:
        nonlocal next_label_number
        label = Label(f'L{next_label_number}')
        next_label_number += 1
        return label
    
    def visit(node: Expression) -> IRVar:
        match node:
            case Literal():
                var = new_var()
                instructions.append(LoadIntConst(node.value, var))
                return var
            
            case BinaryOp():
                var_left = visit(node.left)
                var_right = visit(node.right)
                var_result = new_var()
                instructions.append(Call(
                    fun=IRVar(node.op),
                    args=[var_left, var_right],
                    dest=var_result
                ))
                return var_result
            
            case IfExpression():
                if node.else_clause is None:
                    raise Exception("TODO: handle")
                else:
                    l_then = new_label()
                    l_else = new_label()
                    l_end = new_label()

                    var_cond = visit(node.cond)
                    instructions.append(CondJump(var_cond, l_then, l_else))

                    instructions.append(l_then)
                    var_result = visit(node.then_clause)
                    instructions.append(Jump(l_end))

                    instructions.append(l_else)
                    var_else_result = visit(node.else_clause)
                    instructions.append(Copy(var_else_result, var_result))

                    instructions.append(l_end)
                    return var_result
                
            case _:
                raise Exception(f'Unsupported AST node: {node}')
            
    var_result = visit(root_node)

    # TODO: handle bool and unit results
    instructions.append(Call(
        IRVar("print_int"),
        [var_result],
        new_var()
    ))

    return instructions
