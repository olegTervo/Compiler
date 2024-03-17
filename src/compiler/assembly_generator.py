
import dataclasses
from compiler.ir_generator import *
from compiler.intrinsics import IntrinsicArgs, all_intrinsics

def generate_assembly(instructions: dict[str, list[Instruction]]) -> str:
    assembly_code_lines = []
    def emit(line: str) -> None: assembly_code_lines.append(line)

    locals_all: list[IRVar] = []
    locals_all = get_all_ir_variables(instructions["main"])
    locals = Locals(locals_all) 

    emit('.extern print_int')
    emit('.extern print_bool')
    emit('.extern read_int')

    for entry in instructions.keys():
        emit(f'.global {entry}')
        emit(f'.type {entry}, @function')

    emit('.section .text')
    emit("")
    
    def emit_prologue(name:str, vars: Locals) -> None:
        emit(f'{name}:')
        emit('pushq %rbp') # stores the value of the stack base pointer on the stack
        emit('movq %rsp, %rbp') # copies %rsp to %rbp
        emit(f'subq ${vars.stack_used()}, %rsp') # reserve n bytes for locals
    
    def emit_epilogue() -> None:
        emit('movq %rbp, %rsp')
        emit('popq %rbp')
        emit('ret')
        emit('')

    def emit_function(instructions: list[Instruction], vars: Locals, params: Locals = Locals([])) -> None:
        for inst in instructions:
            emit("")
            emit('# ' + str(inst))
            match inst:
                case Label():
                    emit(f'.L{inst.name}:')

                case LoadIntConst():
                    # TODO: inst is too large or small, limitations
                    if -2**31 <= inst.value < 2**31:
                        emit(f'movq ${inst.value}, {vars.get_ref(inst.dest)}')
                    else:
                        # Due to a quirk of x86-64, we must use
                        # a different instruction for large integers.
                        # It can only write to a register,
                        # not a memory location, so we use %rax
                        # as a temporary.
                        emit(f'movabsq ${inst.value}, %rax')
                        emit(f'movq %rax, {vars.get_ref(inst.dest)}')

                case LoadBoolConst():
                    val = 0
                    if inst.value:
                        val = 1
                    emit(f'movq ${val}, {vars.get_ref(inst.dest)}')
                        
                case Copy():
                    emit(f'movq {vars.get_ref(inst.source)}, %rax')
                    emit(f'movq %rax, {vars.get_ref(inst.dest)}')

                case Call():
                    if (intrinsic := all_intrinsics.get(inst.fun.name)) is not None:
                        args = IntrinsicArgs(
                            arg_refs=[vars.get_ref(a) for a in inst.args],
                            result_register='%rax',
                            emit=emit
                        )
                        intrinsic(args)
                        emit(f'movq %rax, {vars.get_ref(inst.dest)}')
                    else:
                        # assert inst.fun.name in ['print_int', 'print_bool', 'read_int']
                        if len(inst.args) == 1 and inst.fun.name in ['print_int', 'print_bool']:
                            emit(f'movq {vars.get_ref(inst.args[0])}, %rdi') # they are using rdi
                            emit(f'call {inst.fun.name}')
                        elif len(inst.args) == 0:
                            emit(f'call {inst.fun.name}')
                            emit(f'movq %rax, {vars.get_ref(inst.dest)}')
                        else:
                            for arg in inst.args:
                                emit(f'pushq {vars.get_ref(arg)}') # other functions are using stack for all arguments to allow recursion
                            if len(inst.args) % 2 == 1:
                                emit('subq $8, %rsp') # make %rsp % 16 = 0
                            emit(f'call {inst.fun.name}')
                            emit(f'movq %rax, {vars.get_ref(inst.dest)}')

                case Jump():
                    emit(f'jmp .L{inst.label.name}')

                case CondJump():
                    emit(f'cmpq $0, {vars.get_ref(inst.cond)}')
                    emit(f'jne .L{inst.then_label.name}')
                    emit(f'jmp .L{inst.else_label.name}')

                case Return():
                    if inst.val is not None:
                        emit(f'movq {vars.get_ref(inst.val)}, %rax')
                
                case _:
                    raise Exception(f'Unknown instruction: {type(inst)}')

    for entry in instructions.keys():
        if entry != "main":
            emit_prologue(entry, Locals(get_all_ir_variables(instructions[entry])))
            emit_function(instructions[entry], Locals(get_all_ir_variables(instructions[entry])))
            emit_epilogue()

    emit_prologue("main", locals)
    emit('')
    emit_function(instructions["main"], locals)
    emit('movq $0, %rax')
    emit_epilogue()

    return "\n".join(assembly_code_lines)

def get_all_ir_variables(instructions: list[Instruction]) -> list[IRVar]:
    result_list: list[IRVar] = []
    result_set: set[IRVar] = set()

    def add(v: IRVar) -> None:
        if not v.name.startswith('p'):
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
        if v.name.startswith('p'):
            num = int(v.name[1:])
            return f'{8 * num + 8}(%rbp)'
        return self._var_to_location[v]

    def stack_used(self) -> int:
        """Returns the number of bytes of stack space needed for the local variables."""
        return self._stack_used