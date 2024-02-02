
from compiler.parser import BinaryOp, Literal, parse
from compiler.tokenizer import tokenize


def test_parser() -> None:
    assert parse(tokenize("1 + 2")) == BinaryOp(
        left= Literal(1),
        op="+",
        right = Literal(2)
    )