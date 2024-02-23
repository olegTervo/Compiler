
from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.type_checker import Bool, Int, Unit, typecheck


def test_type_checker_works() -> None:
    assert typecheck(parse(tokenize('1 + 2'))) == Int

def test_type_checker_binary_op_minus() -> None:
    assert typecheck(parse(tokenize('1 - 2'))) == Int

def test_type_checker_binary_op_multiply() -> None:
    assert typecheck(parse(tokenize('1 * 2'))) == Int

def test_type_checker_binary_op_devide() -> None:
    assert typecheck(parse(tokenize('1 / 2'))) == Int

def test_type_checker_binary_op_modulo() -> None:
    assert typecheck(parse(tokenize('1 % 2'))) == Int

def test_type_checker_binary_op_less() -> None:
    assert typecheck(parse(tokenize('1 < 2'))) == Bool

def test_type_checker_binary_op_more() -> None:
    assert typecheck(parse(tokenize('1 > 2'))) == Bool

def test_type_checker_binary_op_equal() -> None:
    assert typecheck(parse(tokenize('1 == 2'))) == Bool

def test_type_checker_binary_op_equal_with_bool_exp() -> None:
    assert typecheck(parse(tokenize('1 < 2 == true'))) == Bool

def test_type_checker_binary_op_not_equal() -> None:
    assert typecheck(parse(tokenize('1 != 2'))) == Bool

def test_type_checker_binary_op_not_equal_with_bool_exp() -> None:
    assert typecheck(parse(tokenize('1 >= 2 != true'))) == Bool

def test_type_checker_binary_op_or() -> None:
    assert typecheck(parse(tokenize('1 != 2 or 2 != 1'))) == Bool

def test_type_checker_binary_op_and() -> None:
    assert typecheck(parse(tokenize('1 != 2 and 2 != 1'))) == Bool

def test_type_checker_unary_op_minus() -> None:
    assert typecheck(parse(tokenize('-1'))) == Int

def test_type_checker_unary_op_not() -> None:
    assert typecheck(parse(tokenize('not true'))) == Bool

def test_type_checker_bool() -> None:
    assert typecheck(parse(tokenize('1 + 2 < 3'))) == Bool

def test_type_checker_unit() -> None:
    assert typecheck(parse(tokenize('if 1 < 2 then 3'))) == Unit

def test_type_checker_var_int() -> None:
    assert typecheck(parse(tokenize('var a = 1; a'))) == Int

def test_type_checker_var_bool_true() -> None:
    assert typecheck(parse(tokenize('var a = true; a'))) == Bool

def test_type_checker_var_bool_false() -> None:
    assert typecheck(parse(tokenize('var a = false; a'))) == Bool

def test_type_checker_var_bool_exp() -> None:
    assert typecheck(parse(tokenize('var a = 1 <= 2; a'))) == Bool

def test_type_checker_var_unit() -> None:
    assert typecheck(parse(tokenize('var a = {1+2;}; a'))) == Unit

def test_type_checker_if_returns_int() -> None:
    assert typecheck(parse(tokenize('if 1 < 2 then 3 else 4'))) == Int

def test_type_checker_if_returns_bool() -> None:
    assert typecheck(parse(tokenize('if 1 < 2 then 3 < 4 else 4 < 5'))) == Bool

def test_type_checker_while_returns_unit() -> None:
    assert typecheck(parse(tokenize('while true do 3;'))) == Unit

def test_type_checker_block_unit_return_from_block() -> None:
    assert typecheck(parse(tokenize('var a = 1; {a = a+1; a;}'))) == Unit

def test_type_checker_block_unit_return_semicolon_after_block() -> None:
    assert typecheck(parse(tokenize('var a = 1; {a = a+1; a};'))) == Unit

def test_type_checker_block_unit_return_after_block() -> None:
    assert typecheck(parse(tokenize('var a = 1; {a = a+1; a} a;'))) == Unit

def test_type_checker_block_int_return_from_block() -> None:
    assert typecheck(parse(tokenize('var a = 1; {a = a+1; a}'))) == Int

def test_type_checker_block_int_return() -> None:
    assert typecheck(parse(tokenize('var a = 1; {a = a+1; a} a'))) == Int

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