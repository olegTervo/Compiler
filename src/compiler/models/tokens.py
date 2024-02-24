
from dataclasses import dataclass
import re
from typing import Literal, Tuple

TokenType = Literal["int_literal", "identifier", "operator", "punctuation", "end"]

Regexes: list[Tuple[TokenType, re.Pattern[str]]] = [
    ("int_literal", re.compile(r'[0-9]+')),
    ("identifier", re.compile(r'[a-zA-z_][a-zA-z0-9_]*')),
    ("operator", re.compile(r'==|<=|>=|!=|[+\-*\/=><%]')),
    ("punctuation", re.compile(r'[(){},;:]'))
]

@dataclass(frozen=True)
class Token:
    type: TokenType
    text: str