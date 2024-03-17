
from dataclasses import dataclass
import typing

AllowedType = typing.Literal['Int', 'Bool', 'Unit', 'Function']

@dataclass(frozen=True)
class Type:
    "Base class for types"

@dataclass(frozen=True)
class BasicType(Type):
    name: AllowedType

    def __eq__(self, other: typing.Any) -> bool:
        return isinstance(other, BasicType) and self.name == other.name        

    def __str__(self) -> str:
        return self.name

Int = BasicType('Int')
Bool = BasicType('Bool')
Unit = BasicType('Unit')
FunType = BasicType('Function')

def string_to_type(s: str) -> BasicType:
    match s:
        case 'Int': return Int
        case 'Bool': return Bool
        case 'Unit': return Unit
        case 'Function': return FunType
        case _: raise Exception(f'Type {s} is not allowed')