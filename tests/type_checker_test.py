
from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.type_checker import Bool, Int, Unit, typecheck


def test_type_checker_works() -> None:
    assert typecheck(parse(tokenize('1 + 2'))) == Int

def test_type_checker_bool() -> None:
    assert typecheck(parse(tokenize('1 + 2 < 3'))) == Bool

def test_type_checker_unit() -> None:
    assert typecheck(parse(tokenize('if 1 < 2 then 3'))) == Unit

def test_type_checker_if_returns_int() -> None:
    assert typecheck(parse(tokenize('if 1 < 2 then 3 else 4'))) == Int

def test_type_checker_if_returns_bool() -> None:
    assert typecheck(parse(tokenize('if 1 < 2 then 3 < 4 else 4 < 5'))) == Bool

def test_type_check_can_fail() -> None:
    assert_type_checker_fails('(1 < 2) + 3')

def test_type_check_fails_if_condition_not_bool() -> None:
    assert_type_checker_fails('if 1 then 3 else 4 < 5')

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