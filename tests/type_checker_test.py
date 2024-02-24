
from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.type_checker import *
from compiler.models.expressions import *

def test_type_checker_works() -> None:
    node = parse(tokenize('1 + 2'))
    assert typecheck(node) == Int
    assert node.type == Int

def test_type_checker_binary_op_minus() -> None:
    node = parse(tokenize('1 - 2'))
    assert typecheck(node) == Int
    assert node.type == Int

def test_type_checker_binary_op_multiply() -> None:
    node = parse(tokenize('1 * 2'))
    assert typecheck(node) == Int
    assert node.type == Int

def test_type_checker_binary_op_devide() -> None:
    node = parse(tokenize('1 / 2'))
    assert typecheck(node) == Int
    assert node.type == Int

def test_type_checker_binary_op_modulo() -> None:
    node = parse(tokenize('1 % 2'))
    assert typecheck(node) == Int
    assert node.type == Int

def test_type_checker_binary_op_less() -> None:
    node = parse(tokenize('1 < 2'))
    assert typecheck(node) == Bool
    assert node.type == Bool

def test_type_checker_binary_op_more() -> None:
    node = parse(tokenize('1 > 2'))
    assert typecheck(node) == Bool
    assert node.type == Bool

def test_type_checker_binary_op_equal() -> None:
    node = parse(tokenize('1 == 2'))
    assert typecheck(node) == Bool
    assert node.type == Bool

def test_type_checker_binary_op_equal_with_bool_exp() -> None:
    node = parse(tokenize('1 < 2 == true'))
    assert typecheck(node) == Bool
    assert node.type == Bool

def test_type_checker_binary_op_not_equal() -> None:
    node = parse(tokenize('1 != 2'))
    assert typecheck(node) == Bool
    assert node.type == Bool

def test_type_checker_binary_op_not_equal_with_bool_exp() -> None:
    node = parse(tokenize('1 >= 2 != true'))
    assert typecheck(node) == Bool
    assert node.type == Bool

def test_type_checker_binary_op_or() -> None:
    node = parse(tokenize('1 != 2 or 2 != 1'))
    assert typecheck(node) == Bool
    assert node.type == Bool

def test_type_checker_binary_op_and() -> None:
    node = parse(tokenize('1 != 2 and 2 != 1'))
    assert typecheck(node) == Bool
    assert node.type == Bool

def test_type_checker_unary_op_minus() -> None:
    node = parse(tokenize('-1'))
    assert typecheck(node) == Int
    assert node.type == Int

def test_type_checker_unary_op_not() -> None:
    node = parse(tokenize('not true'))
    assert typecheck(node) == Bool
    assert node.type == Bool

def test_type_checker_bool() -> None:
    node = parse(tokenize('1 + 2 < 3'))
    assert typecheck(node) == Bool
    assert node.type == Bool

def test_type_checker_unit() -> None:
    node = parse(tokenize('if 1 < 2 then 3'))
    assert typecheck(node) == Unit
    assert node.type == Unit

def test_type_checker_var_int() -> None:
    node = parse(tokenize('var a = 1; a'))
    assert typecheck(node) == Int
    assert node.type == Int

def test_type_checker_var_bool_true() -> None:
    node = parse(tokenize('var a = true; a'))
    assert typecheck(node) == Bool
    assert node.type == Bool

def test_type_checker_var_bool_false() -> None:
    node = parse(tokenize('var a = false; a'))
    assert typecheck(node) == Bool
    assert node.type == Bool

def test_type_checker_var_bool_exp() -> None:
    node = parse(tokenize('var a = 1 <= 2; a'))
    assert typecheck(node) == Bool
    assert node.type == Bool

def test_type_checker_var_unit() -> None:
    node = parse(tokenize('var a = {1+2;}; a'))
    assert typecheck(node) == Unit
    assert node.type == Unit

def test_type_checker_if_returns_int() -> None:
    node = parse(tokenize('if 1 < 2 then 3 else 4'))
    assert typecheck(node) == Int
    assert node.type == Int

def test_type_checker_if_returns_bool() -> None:
    node = parse(tokenize('if 1 < 2 then 3 < 4 else 4 < 5'))
    assert typecheck(node) == Bool
    assert node.type == Bool

def test_type_checker_while_returns_unit() -> None:
    node = parse(tokenize('while true do 3;'))
    assert typecheck(node) == Unit
    assert node.type == Unit

def test_type_checker_block_unit_return_from_block() -> None:
    node = parse(tokenize('var a = 1; {a = a+1; a;}'))
    assert typecheck(node) == Unit
    assert node.type == Unit

def test_type_checker_block_unit_return_semicolon_after_block() -> None:
    node = parse(tokenize('var a = 1; {a = a+1; a};'))
    assert typecheck(node) == Unit
    assert node.type == Unit

def test_type_checker_block_unit_return_after_block() -> None:
    node = parse(tokenize('var a = 1; {a = a+1; a} a;'))
    assert typecheck(node) == Unit
    assert node.type == Unit

def test_type_checker_block_int_return_from_block() -> None:
    node = parse(tokenize('var a = 1; {a = a+1; a}'))
    assert typecheck(node) == Int
    assert node.type == Int

def test_type_checker_block_int_return() -> None:
    node = parse(tokenize('var a = 1; {a = a+1; a} a'))
    assert typecheck(node) == Int
    assert node.type == Int
    assert isinstance(node, Block)
    assert len(node.sequence) == 3
    assert node.sequence[0].type == Unit
    assert node.sequence[1].type == Int
    assert node.sequence[2].type == Int

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

def assert_type_checker_fails(code: str) -> None:
    expr = parse(tokenize(code))
    failed = False
    try:
        typecheck(expr)
    except Exception:
        failed = True
    assert failed, f'Type-checking succeeded for: {code}'