from pytest import MonkeyPatch

from compiler.interpreter import interpret
from compiler.parser import parse
from compiler.tokenizer import tokenize


def test_interpreter_works() -> None:
    assert interpret(parse(tokenize('1+2'))) == 3

def test_interpreter_counts() -> None:
    assert interpret(parse(tokenize('1 + 2 * 3'))) == 7

def test_interpreter_unary_minus() -> None:
    assert interpret(parse(tokenize('-1'))) == -1

def test_interpreter_unary_not() -> None:
    assert interpret(parse(tokenize('not true'))) == False

def test_interpreter_unary_not_number() -> None:
    assert interpret(parse(tokenize('not 1'))) == -1

def test_interpreter_counts_bad_expressions() -> None:
    assert interpret(parse(tokenize('1 + (2 < 3)'))) == 2

def test_interpreter_handles_many_expressions() -> None:
    assert interpret(parse(tokenize('1 + 2; 2 - 3; 4'))) == 4

def test_interpreter_handles_if_then() -> None:
    assert interpret(parse(tokenize('if 1 < 2 then 3 else 4'))) == 3

def test_interpreter_handles_if_else() -> None:
    assert interpret(parse(tokenize('if 1 > 2 then 3 else 4'))) == 4

def test_interpreter_handles_while() -> None:
    assert interpret(parse(tokenize('var a = 1; while a < 3 do a = 3;'))) == None

def test_interpreter_handles_while_with_return() -> None:
    assert interpret(parse(tokenize('var a = 1; while a < 3 do { a = a + 1; a }'))) == None
    
def test_interpreter_handles_while_with_blocks() -> None:
    assert interpret(parse(tokenize('var a = 1; while { a < 3 } do { a = a + 1; }'))) == None
    
def test_interpreter_handles_while_then_expression() -> None:
    assert interpret(parse(tokenize('var a = 1; while a < 3 do a = a + 1; a'))) == 3

def test_interpreter_handles_if_in_expression() -> None:
    assert interpret(parse(tokenize('7 + if 1 < 2 then 3 else 4'))) == 10

def test_interpreter_handles_variable_declaration() -> None:
    assert interpret(parse(tokenize('var a = 1'))) == None

def test_interpreter_handles_variable_declaration_and_change() -> None:
    assert interpret(parse(tokenize('var a = 1; a = a + 2; a'))) == 3

def test_interpreter_handles_variable_declaration_shadowing_and_change() -> None:
    assert interpret(parse(tokenize('var a = 1; { var a = 2; a = a + 1; } a = a + 1; a'))) == 2

def test_interpreter_handles_variable_declaration_shadowing_using_itself_and_change() -> None:
    assert interpret(parse(tokenize('var a = 1; a = { var a = a + 5; a = a + 5; a} a'))) == 11

def test_interpreter_handles_variable_declaration_and_use() -> None:
    assert interpret(parse(tokenize('var a = 1; a + 2'))) == 3

def test_interpreter_handles_shadow_variable_declaration_and_use() -> None:
    assert interpret(parse(tokenize('var a = 1; { var a = 2; a + 1 } a + 2'))) == 3

def test_interpreter_handles_block() -> None:
    assert interpret(parse(tokenize('{1 + 2}'))) == 3

def test_interpreter_handles_block_with_many_expressions() -> None:
    assert interpret(parse(tokenize('{1 + 2; 2 - 3; 4}'))) == 4

def test_interpreter_handles_block_with_unit_return() -> None:
    assert interpret(parse(tokenize('{1 + 2; 2 - 3; 4;}'))) == None

def test_interpreter_handles_and_true() -> None:
    assert interpret(parse(tokenize('true and true'))) == True

def test_interpreter_handles_and_false() -> None:
    assert interpret(parse(tokenize('false and true'))) == False

def test_interpreter_handles_or_true() -> None:
    assert interpret(parse(tokenize('true or false'))) == True

def test_interpreter_handles_or_false() -> None:
    assert interpret(parse(tokenize('false or false'))) == False

def test_interpreter_handles_print_int() -> None:
    assert interpret(parse(tokenize('print_int(1)'))) == None

def test_interpreter_handles_print_bool() -> None:
    assert interpret(parse(tokenize('print_bool(true)'))) == None

def test_interpreter_handles_read_int(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr('builtins.input', lambda _: "1")
    assert interpret(parse(tokenize('read_int()'))) == 1

def test_interpreter_fails_bad_parameters_for_predefined_functions() -> None:
    assert_interpreter_fails('print_int()')
    assert_interpreter_fails('print_int(a)')
    assert_interpreter_fails('print_int(1, 2)')
    assert_interpreter_fails('print_bool()')
    assert_interpreter_fails('print_bool(b)')
    assert_interpreter_fails('print_bool(true, false)')

def test_interpreter_fails_bad_input(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr('builtins.input', lambda _: "hi")
    assert_interpreter_fails('read_int()')
    
def test_interpreter_handles_or_expression_from_example() -> None:
    assert interpret(parse(tokenize(
        """ var evaluated_right_hand_side = false;
            true or { evaluated_right_hand_side = true; true };
            evaluated_right_hand_side  // Should be false
        """
    ))) == False

def test_interpreter_fails() -> None:
    assert_interpreter_fails('var a = 1; {var a = 2; var b = 3; a} b')

def assert_interpreter_fails(code: str) -> None:
    node = parse(tokenize(code))
    failed = False
    try:
        interpret(node)
    except Exception: # TODO: Exception types
        failed = True
    assert failed, f'Parsing succeeded for: {code}'