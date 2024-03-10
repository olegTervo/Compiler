
from compiler.models.tokens import Token
from compiler.tokenizer import tokenize


def test_tokenizer_works() -> None:
    assert tokenize("hello") == [
        Token(type="identifier", text="hello")
    ]

def test_tokenizer_whitespace() -> None:
    assert tokenize("   \n\n  hi\n  ") == [
        Token(type="identifier", text="hi")
    ]

def test_tokenizer_number() -> None:
    assert tokenize(" this is 1 ") == [
        Token(type="identifier", text="this"),
        Token(type="identifier", text="is"),
        Token(type="int_literal", text="1")
    ]

def test_tokenizer_operator() -> None:
    assert tokenize("3 + -5") == [
        Token(type="int_literal", text="3"),
        Token(type="operator", text="+"),
        Token(type="operator", text="-"),
        Token(type="int_literal", text="5")
    ]

def test_tokenizer_punctuation() -> None:
    assert tokenize("(2+2)*2") == [
        Token(type="punctuation", text="("),
        Token(type="int_literal", text="2"),
        Token(type="operator", text="+"),
        Token(type="int_literal", text="2"),
        Token(type="punctuation", text=")"),
        Token(type="operator", text="*"),
        Token(type="int_literal", text="2")
    ]

def test_tokenizer_negative_or_substitution() -> None:
    assert tokenize("3-2") == [
        Token(type="int_literal", text="3"),
        Token(type="operator", text="-"),
        Token(type="int_literal", text="2")
    ]

def test_tokenizer_variable_initialization() -> None:
    assert tokenize("int n = 4;") == [
        Token(type="identifier", text="int"),
        Token(type="identifier", text="n"),
        Token(type="operator", text="="),
        Token(type="int_literal", text="4"),
        Token(type="punctuation", text=";")
    ]

def test_tokenizer_course_example() -> None:
    assert tokenize("if a <= bee then print_int(123)") == [
        Token(type="identifier", text="if"),
        Token(type="identifier", text="a"),
        Token(type="operator", text="<="),
        Token(type="identifier", text="bee"),
        Token(type="identifier", text="then"),
        Token(type="identifier", text="print_int"),
        Token(type="punctuation", text="("),
        Token(type="int_literal", text="123"),
        Token(type="punctuation", text=")")
    ]

def test_tokenizer_skips_comment() -> None:
    assert tokenize("// this is comment \n int a;") == [
        Token(type="identifier", text="int"),
        Token(type="identifier", text="a"),
        Token(type="punctuation", text=";")
    ]

def test_tokenizer_skips_comment_hashtag() -> None:
    assert tokenize("# this is comment \n int a;") == [
        Token(type="identifier", text="int"),
        Token(type="identifier", text="a"),
        Token(type="punctuation", text=";")
    ]