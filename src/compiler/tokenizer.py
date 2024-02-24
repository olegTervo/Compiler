import re
from compiler.models.tokens import Regexes, Token

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