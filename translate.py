from typing import *
from relation import *
import ast
import itertools

# normally I would put in a translation step to a well-defined intermediate, but since
# this is supposed to be short and sweet, we just do a direct translation to closures

# the general pattern here is that we dispatch a translator based on the ast type,
# with the signature (set of variables known to be bonud), and a function
# which is a closure over the next term to be translated.
# this continues until the body is translated, and then each step returns
# a runtime closure (stream) to the caller.

# relation invocations take a runtime continuation (next)

# we use two tools to maek this easier. generate and subexpressions


Construct = Callable[[ArgSet], Stream]
# really a union type of all the GTS nodes
Ast = Any

def format_ast_location(file, a):
    pass
# lineno and col_offset

def is_constant(a) -> bool:
    return isinstance(a, int)
    
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

    # ok, we dont really need to dynamize this, we've already deferred signature
    # generation until the query, so we think that it all should be bound
    def relation_out(self, rel:str, b:ArgSet, next:Construct, args:List[Variable]) -> Stream:
        if rel not in self.scope:
            self.error("no such relation", rel);
        r = self.relations[rel]
            
        if len(args) != len(r.arguments):
            self.error("arity mismatch")

        inbound = {}
        outbound = {}
        const = {}

        for term, target in zip(args, r.arguments):
            if term in b:
                inbound[term] = target
            else:
                if is_constant(term):
                    const[target] = term
                else:
                    outbound[term] = target

        function = r.generate_signature(frozenset(inbound.values()))
        down = next(b.union(frozenset(outbound.values())))
                    
        def handler(f:Frame):
            def unpack(outf:Frame):
                f2 = f.copy()
                for output in outbound:
                    f2[output] = outf[outbound[output]]
                down(f2)

            input_args = const.copy()
            for input in inbound:
                input_args[inbound[input]] = f[input]
            result = function(input_args, unpack)
                
        return handler
                

    # ok, we need to handle the tuple-on-the-left unpacking case
    # targets is a list of assigned values, if we were translating into
    # frames that would give us the equivalence classes we need to express that easily
    def assign(self, a: ast.Assign, next:Construct, b:ArgSet) -> Stream:
        if len(a.targets) != 1:
            self.error("unhandled assignment arity", str(len(a.targets)))
        # iterate over targets
        # we need to make these equivalent
        def finish(b:ArgSet, terms:List[Variable]):
            next()
        
        return self.subexpressions([a.targets[0], a.value], b, finish)

   
    def slice(self, s:ast.Slice, target:Variable, next:Construct, b:ArgSet) -> Stream:
        pass
    
    def unwrap_expr(self, e:ast.Expr, target:Variable, next:Construct, b:ArgSet) -> Stream:
        return self.expression(e.value, target, next, b)

    # it would be nicer here if the target assigned the name
    def constant(self, c:ast.Constant, target:Variable, next:Construct, b:ArgSet) -> Stream:
        return self.relation_out("equals", b, next, (target, c.value))

    def subexpressions(self, a:List[Ast], b:ArgSet, next:Callable[[ArgSet, List[Variable]], Stream]) -> Stream:
        terms = []
        i = a.__iter__()
        def each(b:ArgSet) -> Stream:
            try:
                exp = i.__next__()
                if isinstance(exp, ast.Name):
                    terms.append(exp.id)
                    return each(b)
                else:
                    # self.temp(exp) location
                    v = "temp"
                    return self.expression(exp, v, each, b)                
            except StopIteration:
                return next(b, terms)
        s = each(b)
        return s
    

    def binary(self, a:ast.BinOp, target:Variable, next:Construct, b:ArgSet) -> Stream:
        if type(a.op) not in  self.binops:
            self.error("unsupported binop", a.op)
        op =  self.binops[type(a.op)]
        def tail(b:ArgSet, v:List[Variable]) ->Stream:
            return self.relation_out(op, b, next, v[1:])        
        return self.subexpressions([a.left, a.right], b, tail)
        
    def expression(self, a, target:Variable, next:Construct, b:ArgSet) -> Stream:
        # why is this getting called twice?...its just the unwrap
        print("foo", a)
        if not type(a) in self.expressions:
            self.error("no handler for", str(type(a)))
        return self.expressions[type(a)]( a, target, next, b)
        
    # we're not goign to deal with varargs or kwargs right now
    def call(self, c:ast.Call, target:Variable, next:Construct, b:ArgSet) -> Stream:
        def tail(b:ArgSet, v:List[Variable]) ->Stream:
            return self.relation_out(v[0], b, next, v[1:])
        z = c.args.copy()
        z.insert(0, c.func)
        return self.subexpressions(z, b, tail)
    
    def compare(self, c:ast.Compare, target:Variable, next:Construct, b:ArgSet) -> Stream:
        if len(c.comparators) > 1 or len(c.ops) > 1:
            self.error("compound comparator")
        print ("compare", self.comparators[type(c.ops[0])])
        j = c.comparators.copy()
        j.insert(0, c.left)
        def tail(b:ArgSet, t:List[Variable]) -> Stream:
            return next(b)
        return self.subexpressions(j, b, tail)
            
    def attribute(self, a:ast.Attribute, target:Variable, next:Construct, b:ArgSet) -> Stream:
        # a.ctx  ∈ {Load, Store, Del }        
        def tail(b:ArgSet, terms:List[Variable]):
            return self.relation_out("map", b, next, terms)

        return self.subexpressions([a.value, a.attr], b, tail)            

    def if_to_clause(self, i:ast.IfExp, next:Construct, b:ArgSet) -> Stream:
        # i.orelse
        print("if", self.expression(i.test, cond, b), self.body_to_clause(i.body, b, next))

    def statement(self, a, next:Construct, b:ArgSet) -> Stream:
        if type(a) in self.statements:
            print("statement ", type(a))
            return self.statements[type(a)](a, next, b)            
        return self.expression(a, '_', next, b)

    # why doesnt this take a generator next
    # defer translation until runtime to allow for dynamic and late binding
    def body_to_clause(self, body, b:ArgSet, next:Construct) -> Stream:
        i = body.__iter__()
        def each(b:ArgSet) -> Stream:
            try:
                statement = i.__next__()
                print("Statement", statement)                
                return self.statement(statement, each, b)
            except StopIteration:
                # maybe we should think about ... running this instead of just calling next?
                return next(b)
        return each(b)


    def generate(self, body, b:ArgSet) -> RelationStream:
        def head(f:Frame, cont:Stream) -> Stream:
            print("rule head dynamic", f, type(b))
            h = self.body_to_clause( body, b, lambda b:cont)
            h(f)
        return head


# why is posonlyargs here if it seems to be empty when all i have is positional?
def map_arguments(a: ast.arguments):
    result = []
    for i in a.args:
        result.append(i.arg)
    return result
    
# rule should really be a separate layer than ast translation
# we originally passed around our own namespace - and decided to use pythons
class Rule(Relation):
    def __init__(self, d: ast.FunctionDef, filename:str):
        # to support multiple bodies - soft intern a relation, then make an exploder
        # maybe something to uniquify them....like a class relationship? yeah...
        # instead of just dumping them in a bucket and not being able to talk
        # about them individually
        
        # name, args, body, returns, type_comment
        def generate(b:ArgSet) -> RelationStream:
            t = Translate(filename, print)
            return t.generate(d.body, b)

