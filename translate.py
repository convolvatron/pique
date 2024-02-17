from typing import *
from relation import *
import ast

# normally I would put in a translation step to a well-defined intermediate, but since
# this is supposed to be short and sweet, we just do a direct translation to closures

# the general pattern here is that we dispatch a translator based on the ast type,
# with the signature (set of variables known to be bonud), and a function
# which is a closure over the next term to be translated.
# this continues until the body is translated, and then each step returns
# a runtime closure (stream) to the caller.

# relation invocations take a runtime continuation (next)

# we use two tools to make this easier. clause and subexpressions


def listmap(a):
    result = {}
    for i, j in enumerate(a):
        result[i] = j
    return result
    
# really a union type of all the GTS nodes
Ast = Any

def format_ast_location(file, a):
    pass
# lineno and col_offset

class Translate:
    filename: str
    # typing around *args is .. what?
    error: Callable[[str], None]

    def __init__(self, filename, scope, error):
        self.filename = filename
        self.error = error
        self.scope = scope
        
        # doesn't need to be dynamic ... it does, these references are closures over self
        self.statements = {ast.Assign:self.assign,
                           ast.If:self.if_to_clause,
                           }
        self.expressions = {ast.Assign:self.assign,
                            ast.Expr:self.unwrap_expr,
                            ast.Call:self.call,
                            ast.Constant:self.constant,                            
                            ast.BinOp:self.binary,                            
                            ast.Attribute:self.attribute,            
                            ast.Compare:self.compare,
                            ast.Slice:self.slice,
                            }
            

        self.comparators = {
            ast.Eq: lambda x,y: x == y,
            ast.NotEq: lambda x,y: x != y,
            ast.Lt: lambda x,y: x < y,
            ast.LtE: lambda x,y: x <= y,
            ast.Gt: lambda x,y: x > y,
            ast.GtE: lambda x,y: x >= y,
            ast.Is: lambda x,y: x is y,
            ast.IsNot: lambda x,y: x is not y,
            ast.In: lambda x,y: x in y,
            ast.NotIn: lambda x,y: x not in y,
        }
        
        # i suppose this could be derived
        self.binops = {
            ast.Add: "add",
            ast.Sub: "sub",
            ast.Mult: "mult",
            ast.Div: "div",
            ast.FloorDiv: "floordiv",
            ast.Mod: "mod",
            ast.Pow: "pow",
            ast.LShift: "lshift",
            ast.RShift: "rshift",
            ast.BitOr: "bitor",
            ast.BitXor: "bitxor",
            ast.BitAnd: "bitand",
            ast.MatMult: "matmult",
    }
                
    def clause(self, rel:str, args:List[Variable]) -> Clause:
        return (Variable(rel), args.copy())
    
    # ok, we need to handle the tuple-on-the-left unpacking case
    # targets is a list of assigned values, if we were translating into
    # frames that would give us the equivalence classes we need to express that easily
    def assign(self, a: ast.Assign) -> List[Clause]:
        if len(a.targets) != 1:
            self.error("unhandled assignment arity", str(len(a.targets)))
        (cls, vs) = self.subexpressions([a.targets[0], a.value])
        cls.append(self.clause("equals", vs))
        return cls

   
    def slice(self, s:ast.Slice, target:Variable) -> List[Clause]:
        pass
    
    def unwrap_expr(self, e:ast.Expr, target:Variable) -> List[Clause]:
        return self.expression(e.value, target)

    # it would be nicer here if the target assigned the name
    def constant(self, c:ast.Constant, target:Variable) -> List[Clause]:
        return self.relation_out("equals", b, next, (target, c.value))

    def subexpressions(self, a:List[Ast]) -> (List[Clause], List[Variable]):
        c = []        
        v = []
        for i in a:
            if isinstance(i, ast.Name):
                v.append(Variable(i.id))
            else:
                v.append("temp")
                c.append(self.expression(i, v))
        return (c, v)
    
    def binary(self, a:ast.BinOp, target:Variable) -> List[Clause]:
        if type(a.op) not in  self.binops:
            self.error("unsupported binop", a.op)
        op =  self.binops[type(a.op)]
        (prefix, vars) = self.subexpressions([a.left, a.right], b, tail)        
        return prefix.apppend(clause(op, vars))
        
    def expression(self, a, target:Variable) -> List[Clause]:
        print("expression", a)
        if not type(a) in self.expressions:
            panic("foo", type(a))
            self.error("no handler for", str(type(a)))
        return self.expressions[type(a)]( a, target)
        
    def call(self, c:ast.Call, target:Variable) -> List[Clause]:
        (prefix, vars) = self.subexpressions(c.args)
        z = listmap(vars)
        # xxx - free or derived rel
        print("call", c.func.id)
        c = self.clause(c.func.id, z)
        prefix.append(c)
        return prefix
    
    def compare(self, c:ast.Compare, target:Variable) -> List[Clause]:
        if len(c.comparators) > 1 or len(c.ops) > 1:
            self.error("compound comparator")
        j = c.comparators.copy()
        j.insert(0, c.left)
        (prefix, vars) = self.subexpressions(j, b, tail)
        return prefix
            
    def attribute(self, a:ast.Attribute, target:Variable) -> List[Clause]:
        # a.ctx  ∈ {Load, Store, Del }        
        (prefix, vars) = self.subexpressions([a.value, a.attr])
        prefix.append(self.relation_out("map", terms))

    def if_to_clause(self, i:ast.IfExp) -> List[Clause]:
        # i.orelse
        print("if", self.expression(i.test, cond), self.body_to_clause(i.body))

    def statement(self, a) -> List[Clause]:
        if type(a) in self.statements:
            return self.statements[type(a)](a)
        # terminus variable
        return self.expression(a, '_')

    def body_to_clauses(self, body) -> List[Clause]:
        result = []
        for i in body:
            n = self.statement(i)
            result += n
        return result
