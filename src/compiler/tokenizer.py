from dataclasses import dataclass
import re
from typing import Literal, Tuple


TokenType = Literal["int_literal", "identifier", "operator", "punctuation", "end"]

Regexes: list[Tuple[TokenType, re.Pattern[str]]] = [
    ("int_literal", re.compile(r'[0-9]+')),
    ("identifier", re.compile(r'[a-zA-z_][a-zA-z0-9_]*')),
    ("operator", re.compile(r'==|<=|>=|!=|[+\-*\/=><%]')),
    ("punctuation", re.compile(r'[(){},;]'))
]

@dataclass(frozen=True)
class Token:
    type: TokenType
    text: str

def tokenize(source_code: str) -> list[Token]:
    whitespace_re = re.compile(r'\s+')
    comment_re = re.compile(r'//.*\n')
    position = 0
    result: list[Token] = []
    
    while position < len(source_code):
        # skip whitespace matches
        match = whitespace_re.match(source_code, position)
        if match is not None:
            position = match.end()
            continue
        # skip comments
        match = comment_re.match(source_code, position)
        if match is not None:
            position = match.end()
            continue
        
        toAdd = try_match(source_code, position)
        result.append(toAdd)
        position = position + len(toAdd.text)


    return result

def try_match(source_code: str, pointer: int) -> Token:
    for (type, pattern) in Regexes:
        pattern_match = pattern.match(source_code, pointer)
        if pattern_match is not None:
            return Token(type=type, text=source_code[pointer:pattern_match.end()])
        
    raise Exception(f'Tokenization failed near {source_code[pointer:pointer+10]}')