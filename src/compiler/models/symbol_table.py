
from dataclasses import dataclass

@dataclass
class SymTab():
    variables: dict

@dataclass
class HierarchicalSymTab(SymTab):
    parent: SymTab