import sys
from compiler.assembler import assemble
from compiler.assembly_generator import generate_assembly
from compiler.ir_generator import generate_ir
from compiler.parser import parse

from compiler.tokenizer import tokenize
from compiler.type_checker import typecheck

# TODO(student): add more commands as needed
usage = f"""
Usage: {sys.argv[0]} <command> [source_code_file]

Command 'interpret':
    Runs the interpreter on source code.

Common arguments:
    source_code_file        Optional. Defaults to standard input if missing.
 """.strip() + "\n"


def main() -> int:
    command: str | None = None
    input_file: str | None = None
    for arg in sys.argv[1:]:
        if arg in ['-h', '--help']:
            print(usage)
            return 0
        elif arg.startswith('-'):
            raise Exception(f"Unknown argument: {arg}")
        elif command is None:
            command = arg
        elif input_file is None:
            input_file = arg
        else:
            raise Exception("Multiple input files not supported")

    def read_source_code() -> str:
        if input_file is not None:
            with open(input_file) as f:
                return f.read()
        else:
            return sys.stdin.read()

    if command is None:
        print(f"Error: command argument missing\n\n{usage}", file=sys.stderr)
        return 1

    if command == 'interpret':
        source_code = read_source_code()
        ...  # TODO(student)
    elif command == 'ir':
        source_code = read_source_code()
        tokens = tokenize(source_code)
        ast_node = parse(tokens)
        typecheck(ast_node)
        ir_instructions = generate_ir(ast_node)

        for entry in ir_instructions.keys():
            print(entry)
            print("\n".join([str(ins) for ins in ir_instructions[entry]]))
    elif command == 'asm':
        source_code = read_source_code()
        tokens = tokenize(source_code)
        ast_node = parse(tokens)
        typecheck(ast_node)
        ir_instructions = generate_ir(ast_node)
        asm_code = generate_assembly(ir_instructions)
        print(asm_code)
    elif command == 'compile':
        source_code = read_source_code()
        tokens = tokenize(source_code)
        ast_node = parse(tokens)
        typecheck(ast_node)
        ir_instructions = generate_ir(ast_node)
        asm_code = generate_assembly(ir_instructions)
        print(asm_code)
        assemble(asm_code, 'compiled_program')
    elif command == 'test':
        source_code = '''
        .extern print_int
        .extern print_bool
        .extern read_int
        .global vec_len_squared
        .type vec_len_squared, @function
        .global main
        .type main, @function
        .section .text

        vec_len_squared:
        # print 3 sp -8 added ret addr 
        movq %rsp, %rdi
        call print_int

        pushq %rbp
        movq %rsp, %rbp
        subq $8, %rsp

        # print 4 fun stack base -8 added caller bp
        movq %rbp, %rdi
        call print_int
        # print 5 fun sp -8 booked space
        movq %rsp, %rdi
        call print_int

        # print 6 p1
        movq 16(%rbp), %rdi
        call print_int
        # print 7 p2
        movq 24(%rbp), %rdi
        call print_int
        
        # Call(+, [p1, p2], x2)
        movq 16(%rbp), %rax
        addq 24(%rbp), %rax
        movq %rax, -8(%rbp)

        # Call(print_int, [x2], x1)
        movq -8(%rbp), %rdi
        call print_int

        # Return()
        movq %rbp, %rsp
        popq %rbp
        ret

        main:
        pushq %rbp
        movq %rsp, %rbp
        subq $16, %rsp

        # print 1 main stack base
        movq %rbp, %rdi
        call print_int

        # Label(start)
        .Lstart:

        # LoadIntConst(3, x4)
        movq $3, -8(%rbp)

        # LoadIntConst(4, x5)
        movq $4, -16(%rbp)

        # Call(vec_len_squared, [x4, x5], x3)
        pushq -16(%rbp)
        pushq -8(%rbp)
        # subq $8, %rsp
        # print 2 sp is -32, locals and params
        movq %rsp, %rdi
        call print_int
        call vec_len_squared

        # Return()
        movq $0, %rax
        movq %rbp, %rsp
        popq %rbp
        ret

        '''
        assemble(source_code, 'compiled_program')
    else:
        print(f"Error: unknown command: {command}\n\n{usage}", file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
