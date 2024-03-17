
from pytest import MonkeyPatch
from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.type_checker import *
from compiler.models.expressions import *

def test_type_checker_works() -> None:
    node = parse(tokenize('1 + 2'))
    assert typecheck(node) == Int
    assert node.sequence[0].type == Int

def test_type_checker_binary_op_minus() -> None:
    node = parse(tokenize('1 - 2'))
    assert typecheck(node) == Int
    assert node.sequence[0].type == Int

def test_type_checker_binary_op_multiply() -> None:
    node = parse(tokenize('1 * 2'))
    assert typecheck(node) == Int
    assert node.sequence[0].type == Int

def test_type_checker_binary_op_devide() -> None:
    node = parse(tokenize('1 / 2'))
    assert typecheck(node) == Int
    assert node.sequence[0].type == Int

def test_type_checker_binary_op_modulo() -> None:
    node = parse(tokenize('1 % 2'))
    assert typecheck(node) == Int
    assert node.sequence[0].type == Int

def test_type_checker_binary_op_less() -> None:
    node = parse(tokenize('1 < 2'))
    assert typecheck(node) == Bool
    assert node.sequence[0].type == Bool

def test_type_checker_binary_op_more() -> None:
    node = parse(tokenize('1 > 2'))
    assert typecheck(node) == Bool
    assert node.sequence[0].type == Bool

def test_type_checker_binary_op_equal() -> None:
    node = parse(tokenize('1 == 2'))
    assert typecheck(node) == Bool
    assert node.sequence[0].type == Bool

def test_type_checker_binary_op_equal_with_bool_exp() -> None:
    node = parse(tokenize('1 < 2 == true'))
    assert typecheck(node) == Bool
    assert node.sequence[0].type == Bool

def test_type_checker_binary_op_not_equal() -> None:
    node = parse(tokenize('1 != 2'))
    assert typecheck(node) == Bool
    assert node.sequence[0].type == Bool

def test_type_checker_binary_op_not_equal_with_bool_exp() -> None:
    node = parse(tokenize('1 >= 2 != true'))
    assert typecheck(node) == Bool
    assert node.sequence[0].type == Bool

def test_type_checker_binary_op_or() -> None:
    node = parse(tokenize('1 != 2 or 2 != 1'))
    assert typecheck(node) == Bool
    assert node.sequence[0].type == Bool

def test_type_checker_binary_op_and() -> None:
    node = parse(tokenize('1 != 2 and 2 != 1'))
    assert typecheck(node) == Bool
    assert node.sequence[0].type == Bool

def test_type_checker_unary_op_minus() -> None:
    node = parse(tokenize('-1'))
    assert typecheck(node) == Int
    assert node.sequence[0].type == Int

def test_type_checker_unary_op_not() -> None:
    node = parse(tokenize('not true'))
    assert typecheck(node) == Bool
    assert node.sequence[0].type == Bool

def test_type_checker_bool() -> None:
    node = parse(tokenize('1 + 2 < 3'))
    assert typecheck(node) == Bool
    assert node.sequence[0].type == Bool

def test_type_checker_unit() -> None:
    node = parse(tokenize('if 1 < 2 then 3'))
    assert typecheck(node) == Unit
    assert node.sequence[0].type == Unit

def test_type_checker_var_int() -> None:
    node = parse(tokenize('var a = 1; a'))
    assert typecheck(node) == Int
    assert node.sequence[0].type == Int

def test_type_checker_var_bool_true() -> None:
    node = parse(tokenize('var a = true; a'))
    assert typecheck(node) == Bool
    assert node.sequence[0].type == Bool

def test_type_checker_var_bool_false() -> None:
    node = parse(tokenize('var a = false; a'))
    assert typecheck(node) == Bool
    assert node.sequence[0].type == Bool

def test_type_checker_var_bool_exp() -> None:
    node = parse(tokenize('var a = 1 <= 2; a'))
    assert typecheck(node) == Bool
    assert node.sequence[0].type == Bool

def test_type_checker_var_unit() -> None:
    node = parse(tokenize('var a = {1+2;}; a'))
    assert typecheck(node) == Unit
    assert node.sequence[0].type == Unit

def test_type_checker_if_returns_int() -> None:
    node = parse(tokenize('if 1 < 2 then 3 else 4'))
    assert typecheck(node) == Int
    assert node.sequence[0].type == Int

def test_type_checker_if_returns_bool() -> None:
    node = parse(tokenize('if 1 < 2 then 3 < 4 else 4 < 5'))
    assert typecheck(node) == Bool
    assert node.sequence[0].type == Bool

def test_type_checker_while_returns_unit() -> None:
    node = parse(tokenize('while true do 3;'))
    assert typecheck(node) == Unit
    assert node.sequence[0].type == Unit

def test_type_checker_block_unit_return_from_block() -> None:
    node = parse(tokenize('var a = 1; {a = a+1; a;}'))
    assert typecheck(node) == Unit
    assert node.sequence[0].type == Unit

def test_type_checker_block_unit_return_semicolon_after_block() -> None:
    node = parse(tokenize('var a = 1; {a = a+1; a};'))
    assert typecheck(node) == Unit
    assert node.sequence[0].type == Unit

def test_type_checker_block_unit_return_after_block() -> None:
    node = parse(tokenize('var a = 1; {a = a+1; a} a;'))
    assert typecheck(node) == Unit
    assert node.sequence[0].type == Unit

def test_type_checker_block_int_return_from_block() -> None:
    node = parse(tokenize('var a = 1; {a = a+1; a}'))
    assert typecheck(node) == Int
    assert node.sequence[0].type == Int

def test_type_checker_block_int_return() -> None:
    node = parse(tokenize('var a = 1; {a = a+1; a} a'))
    assert typecheck(node) == Int
    assert node.sequence[0].type == Int
    assert isinstance(node.sequence[0], Block)
    assert len(node.sequence[0].sequence) == 3
    assert node.sequence[0].sequence[0].type == Unit
    assert node.sequence[0].sequence[1].type == Int
    assert node.sequence[0].sequence[2].type == Int

def test_type_checker_print_int() -> None:
    node = parse(tokenize('print_int(1)'))
    assert typecheck(node) == Unit
    assert node.sequence[0].type == Unit
    assert isinstance(node.sequence[0], Function)
    assert len(node.sequence[0].args) == 1
    assert node.sequence[0].args[0].type == Int

def test_type_checker_print_bool() -> None:
    node = parse(tokenize('print_bool(true)'))
    assert typecheck(node) == Unit
    assert node.sequence[0].type == Unit
    assert isinstance(node.sequence[0], Function)
    assert len(node.sequence[0].args) == 1
    assert node.sequence[0].args[0].type == Bool

def test_type_checker_read_int(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr('builtins.input', lambda _: "1")
    node = parse(tokenize('read_int()'))
    assert typecheck(node) == Int
    assert node.sequence[0].type == Int
    assert isinstance(node.sequence[0], Function)
    assert len(node.sequence[0].args) == 0

def test_type_checker_module() -> None:
    node = parse(tokenize('''
        fun square(x: Int): Int {
            return x * x;
        }
        
        fun vec_len_squared(x: Int, y: Int): Int {
            return square(x) + square(y);
        }

        fun print_int_twice(x: Int) {
            print_int(x);
            print_int(x);
        }

        vec_len_squared(3, 4)
        '''))
    assert typecheck(node) == Int
    assert len(node.sequence) == 4
    assert node.sequence[0].type == Int
    assert node.sequence[1].type == Int
    assert node.sequence[2].type == Int
    assert node.sequence[3].type == Unit
    assert isinstance(node.sequence[1], FunctionDeclaration)
    assert isinstance(node.sequence[2], FunctionDeclaration)
    assert isinstance(node.sequence[3], FunctionDeclaration)
    assert isinstance(node.sequence[1].body, Block)
    assert isinstance(node.sequence[1].body.sequence[0], ReturnExpression)
    assert node.sequence[1].body.type == Int
    assert node.sequence[1].body.sequence[0].type == Int
    assert isinstance(node.sequence[2].body, Block)
    assert isinstance(node.sequence[2].body.sequence[0], ReturnExpression)
    assert node.sequence[2].body.type == Int
    assert node.sequence[2].body.sequence[0].type == Int
    assert isinstance(node.sequence[3].body, Block)
    assert isinstance(node.sequence[3].body.sequence[0], Function)
    assert isinstance(node.sequence[3].body.sequence[1], Function)
    assert node.sequence[3].body.type == Unit
    assert node.sequence[3].body.sequence[0].type == Unit
    assert node.sequence[3].body.sequence[1].type == Unit


def test_type_check_can_fail() -> None:
    assert_type_checker_fails('(1 < 2) + 3')

def test_type_check_fails_if_condition_not_bool() -> None:
    assert_type_checker_fails('if 1 then 3 else 4 < 5')

def test_type_check_fails_binary_operations_expected_int() -> None:
    assert_type_checker_fails('1 + true')
    assert_type_checker_fails('1 - true')
    assert_type_checker_fails('1 * true')
    assert_type_checker_fails('1 / true')
    assert_type_checker_fails('1 % true')

def test_type_check_fails_binary_operations_expected_bool() -> None:
    assert_type_checker_fails('1 and true')
    assert_type_checker_fails('true or 1')

def test_type_check_fails_unary_operations() -> None:
    assert_type_checker_fails('not 1')
    assert_type_checker_fails('-false')

def test_type_check_fails_different_if_return_types() -> None:
    assert_type_checker_fails('if 1 < 2 then 3 else 4 < 5')

def test_type_checker_fails_print_int_bad_args() -> None:
    assert_type_checker_fails('print_int(true)')
    assert_type_checker_fails('print_int(f())')
    assert_type_checker_fails('print_int(1, 2)')
    assert_type_checker_fails('print_int()')

def test_type_checker_fails_print_bool_bad_args() -> None:
    assert_type_checker_fails('print_bool(1)')
    assert_type_checker_fails('print_bool(f())')
    assert_type_checker_fails('print_bool(true, false)')
    assert_type_checker_fails('print_bool()')

def test_type_checker_fails_read_int_bad_args() -> None:
    assert_type_checker_fails('read_int(1)')
    assert_type_checker_fails('read_int(f())')
    assert_type_checker_fails('read_int(true, false)')
    assert_type_checker_fails('read_int(a)')

def test_type_checker_fails_function_declaration_with_wrong_return_type() -> None:
    assert_type_checker_fails('''
        fun square(x: Int): Bool {
            return x * x;
        }
        
        fun vec_len_squared(x: Int, y: Int): Int {
            return square(x) + square(y);
        }

        vec_len_squared(3, 4)
        ''')
    assert_type_checker_fails('''
        fun square(x: Int) {
            return x * x;
        }
        
        fun vec_len_squared(x: Int, y: Int): Int {
            return square(x) + square(y);
        }

        vec_len_squared(3, 4)
        ''')

def assert_type_checker_fails(code: str) -> None:
    expr = parse(tokenize(code))
    failed = False
    try:
        typecheck(expr)
    except Exception:
        failed = True
    assert failed, f'Type-checking succeeded for: {code}'