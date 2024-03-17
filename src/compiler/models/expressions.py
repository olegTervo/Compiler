from dataclasses import dataclass, field
from compiler.models.types import Type, Unit

@dataclass
class Expression:
    "base class"
    type: Type = field(kw_only=True, default=Unit)

    def ends_with_block(self) -> bool:
        return False
    
    def get_name(self) -> str:
        return ""
    
@dataclass
class TypeExpression(Expression):
    "TODO: separate from generic base class"
    
    def get_name(self) -> str:
        return ""

@dataclass
class Identifier(Expression):
    name: str

    def get_name(self) -> str:
        return self.name

@dataclass
class Literal(Expression):
    value: int | bool | None
    
    def get_name(self) -> str:
        raise Exception("Expression doesn't have name parameter")

@dataclass
class BinaryOp(Expression):
    left: Expression
    op: str
    right: Expression

    def ends_with_block(self) -> bool:
        return isinstance(self.right, Block)
    
    def get_name(self) -> str:
        raise Exception("Expression doesn't have name parameter")

@dataclass
class UnaryOp(Expression):
    op: str
    right: Expression

    def ends_with_block(self) -> bool:
        return isinstance(self.right, Block)
    
    def get_name(self) -> str:
        raise Exception("Expression doesn't have name parameter")

@dataclass
class IfExpression(Expression):
    cond: Expression
    then_clause: Expression
    else_clause: Expression | None

    def ends_with_block(self) -> bool:
        return (isinstance(self.then_clause, Block) and self.else_clause is None) or isinstance(self.else_clause, Block)
    
    def get_name(self) -> str:
        raise Exception("Expression doesn't have name parameter")

@dataclass
class Function(Expression):
    name: str
    args: list[Expression]

    def get_name(self) -> str:
        return self.name
    
@dataclass
class FunctionDeclaration(Expression):
    name: str
    args: list[Expression]
    body: Expression

    def ends_with_block(self) -> bool:
        return isinstance(self.body, Block)
    
    def get_name(self) -> str:
        return self.name

@dataclass
class Block(Expression):
    sequence: list[Expression]

    def ends_with_block(self) -> bool:
        return True
    
    def get_name(self) -> str:
        raise Exception("Expression doesn't have name parameter")
    
@dataclass
class WhileExpression(Expression):
    cond: Expression
    body: Expression

    def ends_with_block(self) -> bool:
        return isinstance(self.body, Block)
    
    def get_name(self) -> str:
        raise Exception("Expression doesn't have name parameter")
    
@dataclass
class VariableDeclaration(Expression):
    name: str
    initializer: Expression

    def get_name(self) -> str:
        return self.name

@dataclass
class Module(Expression):
    "This will allow recoursion function calls, which are restricted in Block"

    sequence: list[Expression]
    
    def get_name(self) -> str:
        raise Exception("Expression doesn't have name parameter")
    
@dataclass
class ReturnExpression(Expression):
    value: Expression
    
    def get_name(self) -> str:
        raise Exception("Expression doesn't have name parameter")