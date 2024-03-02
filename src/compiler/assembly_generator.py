
import dataclasses
from compiler.ir_generator import *
from compiler.intrinsics import IntrinsicArgs, all_intrinsics

def generate_assembly(instructions: list[Instruction]) -> str:
    assembly_code_lines = []
    def emit(line: str) -> None: assembly_code_lines.append(line)

    locals = Locals(get_all_ir_variables(instructions)) 

    emit('.extern print_int')
    emit('.extern print_int')
    emit('.extern read_int')
    emit('.global main')
    emit('.type main, @function')
    
    emit('.section .text')
    emit('main:')
    emit('pushq %rbp')
    emit('movq %rsp, %rbp')
    emit(f'subq ${locals.stack_used()}, %rsp')

    for inst in instructions:
        emit('# ' + str(inst))
        match inst:
            case Label():
                emit(f'.L{inst.name}:')

            case LoadIntConst():
                # TODO: inst is too large or small, limitations
                if -2**31 <= inst.value < 2**31:
                    emit(f'movq ${inst.value}, {locals.get_ref(inst.dest)}')
                else:
                    # Due to a quirk of x86-64, we must use
                    # a different instruction for large integers.
                    # It can only write to a register,
                    # not a memory location, so we use %rax
                    # as a temporary.
                    emit(f'movabsq ${inst.value}, %rax')
                    emit(f'movq %rax, {locals.get_ref(inst.dest)}')

            case LoadBoolConst():
                val = 0
                if inst.value:
                    val = 1
                emit(f'movq ${val}, {locals.get_ref(inst.dest)}')
                    
            case Copy():
                emit(f'movq {locals.get_ref(inst.source)}, %rax')
                emit(f'movq %rax, {locals.get_ref(inst.dest)}')

            case Call():
                if (intrinsic := all_intrinsics.get(inst.fun.name)) is not None:
                    args = IntrinsicArgs(
                        arg_refs=[locals.get_ref(a) for a in inst.args],
                        result_register='%rax',
                        emit=emit
                    )
                    intrinsic(args)
                    emit(f'movq %rax, {locals.get_ref(inst.dest)}')
                else:
                    assert inst.fun.name in ['print_int', 'print_bool', 'read_int']
                    assert len(inst.args) == 1 # TODO: more args
                    emit(f'movq {locals.get_ref(inst.args[0])}, %rdi')
                    emit('call print_int')

            case Jump():
                emit(f'jmp .L{inst.label.name}')

            case CondJump():
                emit(f'cmpq $0, {locals.get_ref(inst.cond)}')
                emit(f'jne .L{inst.then_label.name}')
                emit(f'jmp .L{inst.else_label.name}')

            case Return():
                break
            
            case _:
                raise Exception(f'Unknown instruction: {type(inst)}')

    emit('movq $0, %rax')
    emit('movq %rbp, %rsp')
    emit('popq %rbp')
    emit('ret')
    emit('')

    return "\n".join(assembly_code_lines)

def get_all_ir_variables(instructions: list[Instruction]) -> list[IRVar]:
    result_list: list[IRVar] = []
    result_set: set[IRVar] = set()

    def add(v: IRVar) -> None:
        if v not in result_set:
            result_list.append(v)
            result_set.add(v)

    for insn in instructions:
        for field in dataclasses.fields(insn):
            value = getattr(insn, field.name)
            if isinstance(value, IRVar):
                add(value)
            elif isinstance(value, list):
                for v in value:
                    if isinstance(v, IRVar):
                        add(v)
    return result_list

class Locals:
    """Knows the memory location of every local variable."""
    _var_to_location: dict[IRVar, str]
    _stack_used: int

    def __init__(self, variables: list[IRVar]) -> None:
        self._var_to_location = {}
        self._stack_used = 8 # initialy holds the caller's %rbp
        for v in variables:
            if v not in self._var_to_location:
                self._var_to_location[v] = f'-{self._stack_used}(%rbp)'
                self._stack_used += 8

    def get_ref(self, v: IRVar) -> str:
        """Returns an Assembly reference like `-24(%rbp)`
        for the memory location that stores the given variable"""
        return self._var_to_location[v]

    def stack_used(self) -> int:
        """Returns the number of bytes of stack space needed for the local variables."""
        return self._stack_used