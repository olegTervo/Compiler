
from compiler.parser import BinaryOp, IfExpression, Literal, parse
from compiler.tokenizer import tokenize

def test_parser_can_parse() -> None:
    assert parse(tokenize("1")) == Literal(1)

def test_parser_simple_addition() -> None:
    assert parse(tokenize("1 + 2")) == BinaryOp(
        left= Literal(1),
        op='+',
        right = Literal(2)
    )

def test_parser_complex_addition() -> None:
    assert parse(tokenize("1 + 2 + 3")) == BinaryOp(
        left = BinaryOp(
            left=Literal(1),
            op='+',
            right=Literal(2)
        ),
        op='+',
        right=Literal(3)
    )

def test_parser_different_operators() -> None:
    assert parse(tokenize("1 + 2 - 3")) == BinaryOp(
        left = BinaryOp(
            left=Literal(1),
            op='+',
            right=Literal(2)
        ),
        op='-',
        right=Literal(3)
    )

def test_parser_right_multiplication() -> None:
    assert parse(tokenize("1 + 2 * 3")) == BinaryOp(
        left=Literal(1),
        op='+',
        right=BinaryOp(
            left=Literal(2),
            op='*',
            right=Literal(3)
        ),
    )

def test_parser_right_and_left_multiplication() -> None:
    assert parse(tokenize("1 * 2 + 2 * 3")) == BinaryOp(
        left=BinaryOp(
            left=Literal(1),
            op='*',
            right=Literal(2)
        ),
        op='+',
        right=BinaryOp(
            left=Literal(2),
            op='*',
            right=Literal(3)
        ),
    )

def test_parser_parenthesis() -> None:
    assert parse(tokenize("(2+2)*2")) == BinaryOp(
        left=BinaryOp(
            left=Literal(2),
            op='+',
            right=Literal(2)
        ),
        op='*',
        right=Literal(2)
    )

def test_parser_parenthesis_right() -> None:
    assert parse(tokenize("2 * ( 2 + 2 )")) == BinaryOp(
        left=Literal(2),
        op='*',
        right=BinaryOp(
            left=Literal(2),
            op='+',
            right=Literal(2)
        )
    )

def test_parser_complex_expression() -> None:
    assert parse(tokenize("2 * ( 1 + 3 ) / 4")) == BinaryOp(
        left=BinaryOp(
            left=Literal(2),
            op='*',
            right=BinaryOp(
                left=Literal(1),
                op='+',
                right=Literal(3)
            )
        ),
        op='/',
        right=Literal(4)
    )

def test_parser_comparison() -> None:
    assert parse(tokenize('1 > 2+1')) == BinaryOp(
        left=Literal(1),
        op='>',
        right=BinaryOp(
            left=Literal(2),
            op='+',
            right=Literal(1)
        )
    )

def test_parser_simple_if() -> None:
    assert parse(tokenize('if 1 then 2')) == IfExpression(
        cond=Literal(1),
        then_clause=Literal(2),
        else_clause=None
    )

def test_parser_if_with_expressions() -> None:
    assert parse(tokenize('if 1 + 2 then 2 * 2 else 3 / 3')) == IfExpression(
        cond=BinaryOp(
            left=Literal(1),
            op='+',
            right=Literal(2)
        ),
        then_clause=BinaryOp(
            left=Literal(2),
            op='*',
            right=Literal(2)
        ),
        else_clause=BinaryOp(
            left=Literal(3),
            op='/',
            right=Literal(3)
        )
    )

def test_parser_if_is_a_part_of_expression() -> None:
    assert parse(tokenize('1 + if 1 then 2 else 3')) == BinaryOp(
        left=Literal(1),
        op='+',
        right=IfExpression(
            cond=Literal(1),
            then_clause=Literal(2),
            else_clause=Literal(3)
        )
    )

# TODO: test nested if