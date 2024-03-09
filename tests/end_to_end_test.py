from dataclasses import dataclass
import os
import sys
import subprocess

from compiler.assembler import assemble
from compiler.assembly_generator import generate_assembly
from compiler.ir_generator import generate_ir
from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.type_checker import typecheck

@dataclass
class DataForTest():
    filename: str
    name: str
    code: str
    inputs: list[str]
    outputs: list[str]

directory = os.path.join(os.path.dirname(__file__), '../test_programs')

def parse_test_case(file_name: str, test_case: str, i: int) -> DataForTest:
    code: str = ""
    inputs: list[str] = []
    outputs: list[str] = []
    for line in test_case.split("\n"):
        if line.startswith("input"):
            inputs.append(line[len("input "):])
        elif line.startswith("output"):
            outputs.append(line[len("output "):])
        else:
            code = code + line + "\n"

    return DataForTest(filename=file_name, name=file_name + "_" + str(i), code=code, inputs=inputs, outputs=outputs)

def find_test_cases() -> list[DataForTest]:
    res: list[DataForTest] = []
    files = os.listdir(directory)
    for file_name in files:
        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
                tests = content.split('\n---\n')
                for i in range(0, len(tests)):
                    res.append(parse_test_case(file_name, tests[i], i))

    return res

def test_all() -> None:
    ouput_dir = os.path.join(directory, 'workdir')
    if not os.path.exists(ouput_dir):
        os.makedirs(ouput_dir)

    for test_case in find_test_cases():
        def run_test_case(test_case: DataForTest = test_case) -> None:
            tokens = tokenize(test_case.code)
            ast_node = parse(tokens)
            typecheck(ast_node)
            ir_instructions = generate_ir(ast_node)
            asm_code = generate_assembly(ir_instructions)

            otput_file = os.path.join(ouput_dir, test_case.name)
            assemble(asm_code, f'test_programs/workdir/{test_case.name}')
            
            process = subprocess.Popen(otput_file, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for input_data in test_case.inputs:
                if process.stdin is not None:
                    process.stdin.write(input_data.encode())
                    process.stdin.flush()
                else:
                    raise Exception("Exception on running test case")

            output, error = process.communicate()
            output_str = output.decode()
            assert len(test_case.outputs) == 0 or output_str == '\n'.join(test_case.outputs) + '\n'

        sys.modules[__name__].__setattr__(
            f'test_{test_case.name}',
            run_test_case
        )
        
test_all()
