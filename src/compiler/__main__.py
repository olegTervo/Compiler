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
        print("\n".join([str(ins) for ins in ir_instructions]))
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
        assemble(asm_code, 'compiled_program')
    else:
        print(f"Error: unknown command: {command}\n\n{usage}", file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
