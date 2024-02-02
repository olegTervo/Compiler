
from compiler.interpreter import interpret
from compiler.parser import parse
from compiler.tokenizer import tokenize


def test_interpreter_works() -> None:
    assert interpret(parse(tokenize('1+2'))) == 3

def test_interpreter_counts() -> None:
    assert interpret(parse(tokenize('1 + 2 * 3'))) == 7

def test_interpreter_handles_if_then() -> None:
    assert interpret(parse(tokenize('if 1 < 2 then 3 else 4'))) == 3

def test_interpreter_handles_if_else() -> None:
    assert interpret(parse(tokenize('if 1 > 2 then 3 else 4'))) == 4

def test_interpreter_handles_if_in_expression() -> None:
    assert interpret(parse(tokenize('7 + if 1 < 2 then 3 else 4'))) == 10