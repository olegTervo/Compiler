from dataclasses import dataclass, field
from compiler.models.types import Type, Unit

@dataclass
class Expression:
    "base class"
    type: Type = field(kw_only=True, default=Unit)

    def ends_with_block(self) -> bool:
        return False
    
@dataclass
class TypeExpression(Expression):
    "TODO: separate from generic base class"

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class Literal(Expression):
    value: int | bool | None

@dataclass
class BinaryOp(Expression):
    left: Expression
    op: str
    right: Expression

    def ends_with_block(self) -> bool:
        return isinstance(self.right, Block)

@dataclass
class UnaryOp(Expression):
    op: str
    right: Expression

    def ends_with_block(self) -> bool:
        return isinstance(self.right, Block)

@dataclass
class IfExpression(Expression):
    cond: Expression
    then_clause: Expression
    else_clause: Expression | None

    def ends_with_block(self) -> bool:
        return (isinstance(self.then_clause, Block) and self.else_clause is None) or isinstance(self.else_clause, Block)

@dataclass
class Function(Expression):
    name: str
    args: list[Expression]

@dataclass
class Block(Expression):
    sequence: list[Expression]

    def ends_with_block(self) -> bool:
        return True
    
@dataclass
class WhileExpression(Expression):
    cond: Expression
    body: Expression

    def ends_with_block(self) -> bool:
        return isinstance(self.body, Block)
    
@dataclass
class VariableDeclaration(Expression):
    name: str
    initializer: Expression