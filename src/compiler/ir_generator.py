from compiler.models.expressions import *
from compiler.models.instructions import *
from compiler.models.symbol_table import *
from compiler.models.types import *

RootTypes = {
    IRVar('+'): Int,
    IRVar('-'): Int,
    IRVar('*'): Int,
    IRVar('/'): Int,
    IRVar('<'): Bool,
    IRVar('>'): Bool,
    IRVar('=='): Bool,
    IRVar('>='): Bool,
    IRVar('!='): Bool,
    IRVar('%'): Int,
    IRVar('and'): Bool,
    IRVar('or'): Bool,

    IRVar('unary_not'): Bool,
    IRVar('unary_-'): Int
}

next_var_number = 1
def get_next_var_number() -> int:
    global next_var_number
    ret = next_var_number
    next_var_number = next_var_number + 1
    return ret

end_label_number = 1
def get_next_end_label_number() -> int:
    global end_label_number
    ret = end_label_number
    end_label_number = end_label_number + 1
    return ret

def generate_ir(exp: Expression,  root_types: dict[IRVar, Type] = {}) -> dict[str, list[Instruction]]:
    instructions_dictionary: dict[str, list[Instruction]] = {}   
    var_types: dict[IRVar, Type] = root_types.copy()

    # 'var_unit' is used when an expression's type is 'Unit'.
    var_unit = IRVar('unit')
    var_types[var_unit] = Unit
    
    next_label_number = 1
    next_parameter_number = 1
    instructions: list[Instruction] = []

    def new_var(t: Type) -> IRVar:
        next = get_next_var_number()
        var = IRVar(f'x{next}')
        return var
    
    def new_label() -> Label:
        nonlocal next_label_number
        label = Label(f'L{next_label_number}')
        next_label_number += 1
        return label
    
    def new_parameter() -> IRVar:
        nonlocal next_parameter_number
        parameter = IRVar(f'p{next_parameter_number}')
        next_parameter_number += 1
        return parameter
    
    def reset_parameters() -> None:
        nonlocal next_parameter_number
        next_parameter_number = 1
    
    def visit(node: Expression, variables: SymTab) -> IRVar:
        match node:
            case Literal():
                match node.value:
                    case bool():
                        var = new_var(Bool)
                        instructions.append(LoadBoolConst(node.value, var))
                    case int():
                        var = new_var(Int)
                        instructions.append(LoadIntConst(node.value, var))
                    case None:
                        var = var_unit
                    case _:
                        raise Exception(f"loc(TODO): unsupported literal: {type(node.value)}")
                    
                return var
            
            case Identifier():
                if node.name in variables.variables:
                    return variables.variables[node.name]
                elif isinstance(variables, HierarchicalSymTab):
                    return visit(node, variables.parent)
                else:
                    raise Exception(f'Variable {node.name} is not defined')

            
            case BinaryOp():
                var_left = visit(node.left, variables)

                if isinstance(node.left, Identifier) and node.op == '=':
                    if isinstance(variables.variables, dict) and node.left.name in variables.variables:
                        var_right = visit(node.right, variables)
                        instructions.append(Copy(var_right, variables.variables[node.left.name]))
                        return variables.variables[node.left.name]
                    elif isinstance(variables, HierarchicalSymTab):
                        return visit(node, variables.parent)
                    else:
                        raise Exception(f'Asserting unknown variable {node.left.name}')
                elif node.op == 'and':
                    label_and_right = new_label()
                    label_and_skip = new_label()
                    label_and_end = new_label()
                    instructions.append(CondJump(var_left, label_and_right, label_and_skip))
                    instructions.append(label_and_right)
                    var_right = visit(node.right, variables)
                    var_result = new_var(node.type)
                    instructions.append(Copy(var_right, var_result))
                    instructions.append(Jump(label_and_end))
                    instructions.append(label_and_skip)
                    instructions.append(LoadBoolConst(False, var_result))
                    instructions.append(Jump(label_and_end))
                    instructions.append(label_and_end)
                    return var_result
                elif node.op == 'or':
                    label_or_right = new_label()
                    label_or_skip = new_label()
                    label_or_end = new_label()
                    instructions.append(CondJump(var_left, label_or_skip, label_or_right))
                    instructions.append(label_or_right)
                    var_right = visit(node.right, variables)
                    var_result = new_var(node.type)
                    instructions.append(Copy(var_right, var_result))
                    instructions.append(Jump(label_or_end))
                    instructions.append(label_or_skip)
                    instructions.append(LoadBoolConst(True, var_result))
                    instructions.append(Jump(label_or_end))
                    instructions.append(label_or_end)
                    return var_result

                var_right = visit(node.right, variables)
                var_result = new_var(node.type)
                instructions.append(Call(
                    fun=IRVar(node.op),
                    args=[var_left, var_right],
                    dest=var_result
                ))
                return var_result
            
            case UnaryOp():
                variable = visit(node.right, variables)
                var_result = new_var(node.type)
                if node.type == BasicType('Int'):
                    instructions.append(Call(
                        fun=IRVar('unary_-'),
                        args=[variable],
                        dest=var_result
                    ))
                elif node.type == BasicType('Bool'):
                    instructions.append(Call(
                        fun=IRVar('unary_not'),
                        args=[variable],
                        dest=var_result
                    ))
                else:
                    raise Exception(f'Unknown unary operation {node.op} with node type {node.type}')
                return var_result

            case IfExpression():
                if node.else_clause is None:
                    l_then = new_label()
                    l_end = new_label()

                    var_cond = visit(node.cond, variables)
                    instructions.append(CondJump(var_cond, l_then, l_end))

                    instructions.append(l_then)
                    var_result = visit(node.then_clause, variables)

                    instructions.append(l_end)
                    return var_result
                else:
                    l_then = new_label()
                    l_else = new_label()
                    l_end = new_label()

                    var_cond = visit(node.cond, variables)
                    instructions.append(CondJump(var_cond, l_then, l_else))

                    var_result = new_var(BasicType('Unit'))

                    instructions.append(l_then)
                    var_result_then = visit(node.then_clause, variables)
                    instructions.append(Copy(var_result_then, var_result))
                    instructions.append(Jump(l_end))

                    instructions.append(l_else)
                    var_else_result = visit(node.else_clause, variables)
                    instructions.append(Copy(var_else_result, var_result))

                    instructions.append(l_end)
                    return var_result
                
            case VariableDeclaration():
                last = visit(node.initializer, variables)
                var_result = new_var(node.initializer.type)
                instructions.append(Copy(last, var_result))
                variables.variables[node.name] = var_result
                
                return var_unit

            case Block():
                childVariables = HierarchicalSymTab({}, variables)
                for i in range(0, len(node.sequence)-1):
                    visit(node.sequence[i], childVariables)
                return visit(node.sequence[len(node.sequence)-1], childVariables)
            
            case WhileExpression():
                l_start = new_label()
                l_body = new_label()
                l_end = new_label()

                instructions.append(l_start)
                var_cond = visit(node.cond, variables)
                instructions.append(CondJump(var_cond, l_body, l_end))

                instructions.append(l_body)
                var_result_body = visit(node.body, variables)
                instructions.append(Jump(l_start))

                instructions.append(l_end)
                return var_result_body
            
            case Function():
                if node.name in ['print_int', 'print_bool', 'read_int']:
                    if len(node.args) > 1:
                        raise Exception(f"Invalid arguments for function {node.name}")
                    var_result = new_var(BasicType('Unit'))
                    args = []
                    for arg in node.args:
                        args.append(visit(arg, variables))
                    instructions.append(Call(
                        fun=IRVar(node.name),
                        args=args,
                        dest=var_result
                    ))
                    return var_result
                else:
                    var_result = new_var(node.type)
                    root_variables = variables
                    while isinstance(root_variables, HierarchicalSymTab):
                        root_variables = root_variables.parent
                    args=[]
                    for arg in node.args:
                        args.append(visit(arg, variables))
                    instructions.append(Call(
                        fun=IRVar(node.name),
                        args=args,
                        dest=var_result
                    ))
                    return var_result
                
            case ReturnExpression():
                res = visit(node.value, variables)
                instructions.append(Return(val=res))
                instructions.append(Jump(Label(f"End_{end_label_number}")))
                return res

            case _:
                raise Exception(f'Unsupported AST node: {node}')
            

    root_symtab = SymTab({})
    for v in root_types.keys():
        root_symtab.variables[v.name] = v

    if isinstance(exp, Module):
        root_node = exp.sequence[0]
        for i in range(1, len(exp.sequence)):
            next = exp.sequence[i]
            if isinstance(next, FunctionDeclaration):
                instructions_dictionary[next.name] = generate_ir(next)["main"]
                instructions_dictionary[next.name].append(Label(f"End_{end_label_number}"))
                get_next_end_label_number()
        instructions.append(Label('start'))
    elif isinstance(exp, FunctionDeclaration):
        if len(exp.args) % 2 == 1: new_parameter() # fix for odd amount of parameters to make stack % 16 = 0
        for arg in exp.args:
            ir_var = new_parameter()
            var = new_var(arg.type)
            instructions.append(Copy(ir_var, var))
            root_symtab.variables[arg.get_name()] = var
        reset_parameters()
        root_node = exp.body
    else:
        root_node = exp
        instructions.append(Label('start'))
    
    var_result = visit(root_node, root_symtab)

    if not isinstance(exp, FunctionDeclaration):
        if root_node.type == Int:
            instructions.append(Call(
                IRVar("print_int"),
                [var_result],
                new_var(Unit)
            ))
        elif root_node.type == Bool:
            instructions.append(Call(
                IRVar("print_bool"),
                [var_result],
                new_var(Unit)
            ))

        instructions.append(Return())

    instructions_dictionary["main"] = instructions
    return instructions_dictionary