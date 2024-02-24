
from dataclasses import dataclass
import typing

AllowedType = typing.Literal['Int', 'Bool', 'Unit', 'Function']

@dataclass(frozen=True)
class Type:
    "Base class for types"

@dataclass(frozen=True)
class BasicType(Type):
    name: AllowedType

Int = BasicType('Int')
Bool = BasicType('Bool')
Unit = BasicType('Unit')
FunType = BasicType('Function')

def string_to_type(s: str) -> BasicType:
    match s:
        case 'Int': parsed: AllowedType = 'Int'
        case 'Bool': parsed = 'Bool'
        case 'Unit': parsed = 'Unit'
        case 'Function': parsed = 'Function'
        case _: raise Exception(f'Type {s} is not allowed')
    return BasicType(parsed)