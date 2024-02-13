
from compiler.parser import BinaryOp, Block, Function, Identifier, IfExpression, Literal, UnaryOp, VariableDeclaration, WhileExpression, parse
from compiler.tokenizer import tokenize

def test_parser_can_parse() -> None:
    assert parse(tokenize("1")) == Literal(1)

def test_parser_simple_addition() -> None:
    assert parse(tokenize("1 + 2")) == BinaryOp(
        left= Literal(1),
        op='+',
        right = Literal(2)
    )

def test_parser_increase_variable() -> None:
    assert parse(tokenize("a + 2")) == BinaryOp(
        left= Identifier(name='a'),
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

def test_parser_comparison_smaller_or_equal() -> None:
    assert parse(tokenize('1 <= a+1')) == BinaryOp(
        left=Literal(1),
        op='<=',
        right=BinaryOp(
            left=Identifier(name='a'),
            op='+',
            right=Literal(1)
        )
    )

def test_parser_reminder() -> None:
    assert parse(tokenize('1 % 2')) == BinaryOp(
        left=Literal(1),
        op='%',
        right=Literal(2)
    )

def test_parser_comparison_equality() -> None:
    assert parse(tokenize('1 == a')) == BinaryOp(
        left=Literal(1),
        op='==',
        right=Identifier('a')
    )

def test_parser_binary_logical_or() -> None:
    assert parse(tokenize('if a < b or a < c then 1')) == IfExpression(
        cond=BinaryOp(
            left=BinaryOp(
                left=Identifier('a'),
                op='<',
                right=Identifier('b')
            ),
            op='or',
            right=BinaryOp(
                left=Identifier('a'),
                op='<',
                right=Identifier('c')
            ),
        ),
        then_clause=Literal(1),
        else_clause=None
    )

def test_parser_binary_logical_and() -> None:
    assert parse(tokenize('if a < b and a < c then 1')) == IfExpression(
        cond=BinaryOp(
            left=BinaryOp(
                left=Identifier('a'),
                op='<',
                right=Identifier('b')
            ),
            op='and',
            right=BinaryOp(
                left=Identifier('a'),
                op='<',
                right=Identifier('c')
            ),
        ),
        then_clause=Literal(1),
        else_clause=None
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

def test_parser_function() -> None:
    assert parse(tokenize('f(x)')) == Function(
        name='f',
        args=[Identifier(name='x')]
    )

def test_parser_function_many_arguments() -> None:
    assert parse(tokenize('f(x, y, z)')) == Function(
        name='f',
        args=[
            Identifier(name='x'),
            Identifier(name='y'),
            Identifier(name='z')
            ]
    )

def test_parser_function_expression_argument() -> None:
    assert parse(tokenize('f(1+2)')) == Function(
        name='f',
        args=[
            BinaryOp(
                left=Literal(1),
                op='+',
                right=Literal(2)
            )]
    )

def test_parser_function_complex_arguments() -> None:
    assert parse(tokenize('f(1+2, a, f(1+2))')) == Function(
        name='f',
        args=[
            BinaryOp(
                left=Literal(1),
                op='+',
                right=Literal(2)
            ),
            Identifier(name='a'),
            Function(
                name='f',
                args=[
                    BinaryOp(
                        left=Literal(1),
                        op='+',
                        right=Literal(2)
                    )]
            )]
    )

def test_parser_parse_a_block() -> None:
    assert parse(tokenize('{ 1 }')) == Block([
        Literal(1)
    ])

# TODO: parse empty block
# def test_parser_parse_an_empty_block() -> None:
#     assert parse(tokenize('{ }')) == Block([])

def test_parser_parse_a_block_with_identifier() -> None:
    assert parse(tokenize('{ a }')) == Block([
        Identifier('a')
    ])

def test_parser_parse_a_block_with_expression() -> None:
    assert parse(tokenize('{ 1 + 2 }')) == Block([
        BinaryOp(
            left=Literal(1),
            op='+',
            right=Literal(2)
        )
    ])

def test_parser_parse_a_block_unit_return() -> None:
    assert parse(tokenize('{ 1 + 2; }')) == Block([
        BinaryOp(
            left=Literal(1),
            op='+',
            right=Literal(2)
        ),
        Literal(None)
    ])

def test_parser_parse_blocks() -> None:
    assert parse(tokenize('{ 1 + 2 } { a - b }')) == Block([
        Block([
            BinaryOp(
                left=Literal(1),
                op='+',
                right=Literal(2)
            )
        ]),
        Block([
            BinaryOp(
                left=Identifier('a'),
                op='-',
                right=Identifier('b')
            )
        ])
    ])

def test_parser_parse_blocks_and_expression() -> None:
    assert parse(tokenize(
        """
        { 1 + 2 }
        3;
        { a - b }
        """
        )) == Block([
        Block([
            BinaryOp(
                left=Literal(1),
                op='+',
                right=Literal(2)
            )
        ]),
        Literal(3),
        Block([
            BinaryOp(
                left=Identifier('a'),
                op='-',
                right=Identifier('b')
            )
        ])
    ])

def test_parser_parse_block_in_a_block() -> None:
    assert parse(tokenize('{ { a + b } }')) == Block([
        Block([
            BinaryOp(
                left=Identifier('a'),
                op='+',
                right=Identifier('b')
            )
        ])
    ])

def test_parser_parse_if_with_blocks() -> None:
    assert parse(tokenize('if true then { a } else { b }')) == IfExpression(
        Literal(True),
        then_clause=Block([Identifier('a')]),
        else_clause=Block([Identifier('b')])
    )

def test_parser_parse_block_with_if_with_blocks() -> None:
    assert parse(tokenize('{ if false then { a } else { b } }')) == Block([
        IfExpression(
        cond=Literal(False),
        then_clause=Block([Identifier('a')]),
        else_clause=Block([Identifier('b')])
        )
    ])

def test_parser_parse_expression_in_block_without_semicolon() -> None:
    assert parse(tokenize('{ if true then { a } else { b } 3 }')) == Block([
        IfExpression(
            cond=Literal(True),
            then_clause=Block([Identifier('a')]),
            else_clause=Block([Identifier('b')])
        ),
        Literal(3)
    ])

def test_parser_parse_while() -> None:
    assert parse(tokenize('while a do b')) == WhileExpression(
        cond=Identifier('a'),
        body=Identifier('b')
    )
    
def test_parser_parse_while_with_blocks() -> None:
    assert parse(tokenize('while { a } do { b }')) == WhileExpression(
        cond=Block([Identifier('a')]),
        body=Block([Identifier('b')])
    )
    
def test_parser_parse_while_with_blocks_then_expression() -> None:
    assert parse(tokenize('while { a } do { b } c')) == Block([
        WhileExpression(
            cond=Block([Identifier('a')]),
            body=Block([Identifier('b')])
        ),
        Identifier('c')
    ])

def test_parser_parse_unary_operation() -> None:
    assert parse(tokenize('-a')) == UnaryOp(
        op='-',
        right=Identifier('a')
    )

def test_parser_parse_unary_operation_not() -> None:
    assert parse(tokenize('not a')) == UnaryOp(
        op='not',
        right=Identifier('a')
    )

def test_parser_parse_unary_operation_not_block() -> None:
    assert parse(tokenize('not { a }')) == UnaryOp(
        op='not',
        right=Block([Identifier('a')])
    )

def test_parser_parse_unary_operation_then_literal_no_semicolon() -> None:
    assert parse(tokenize('not { a } b')) == Block([
        UnaryOp(
            op='not',
            right=Block([Identifier('a')])
        ),
        Identifier('b')
    ])

def test_parser_parse_unary_operation_then_literal_after_semicolon() -> None:
    assert parse(tokenize('not { a }; b')) == Block([
        UnaryOp(
            op='not',
            right=Block([Identifier('a')])
        ),
        Identifier('b')
    ])

def test_parser_parse_variable_declaration() -> None:
    assert parse(tokenize('var a = b')) == VariableDeclaration(
        name='a',
        initializer=Identifier('b')
    )

def test_parser_parse_variable_declaration_fails() -> None:
    assert_parser_fails('if var a = b then c')
    assert_parser_fails('while var a = b do c')
    assert_parser_fails('if a then var a = b')
    assert_parser_fails('a = var b = c')
    assert_parser_fails('var a = var b')

def test_parser_parse_assignment() -> None:
    assert parse(tokenize('a = b + 1')) == BinaryOp(
        left=Identifier('a'),
        op='=',
        right=BinaryOp(
            left=Identifier('b'),
            op='+',
            right=Literal(1)
        )
    )

def test_parser_block_test_cases() -> None:
    assert_parser_not_fails('{ { a } { b } }')
    assert_parser_not_fails('{ if true then { a } b }')
    assert_parser_not_fails('{ if true then { a }; b }')
    assert_parser_not_fails('{ if true then { a } b; c }')
    assert_parser_not_fails('{ if true then { a } else { b } 3 }')
    # assert_parser_not_fails('x = { { f(a) } { b } }')

def test_parser_block_test_cases_should_fail() -> None:
    assert_parser_fails('{ a b }')
    assert_parser_fails('{ if true then { a } b c }')

def test_parser_empty_input() -> None:
    assert_parser_fails('')

def test_parser_fails() -> None:
    assert_parser_fails('1 + 3 4')

def assert_parser_fails(code: str) -> None:
    token = tokenize(code)
    failed = False
    try:
        parse(token)
    except Exception: # TODO: Exception types
        failed = True
    assert failed, f'Parsing succeeded for: {code}'

def assert_parser_not_fails(code: str) -> None:
    token = tokenize(code)
    passed = False
    try:
        parse(token)
        passed = True
    except Exception: # TODO: Exception types
        pass
    assert passed, f'Parsing not succeeded for: {code}'

# TODO: test nested if