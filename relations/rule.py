from typing import *
from relation import *

# rule should really be a separate layer than ast translation
# we originally passed around our own namespace - and decided to use pythons
Construct = Callable[[ArgSet], List[Clause]]

class Rule(Relation):
    # what about heads? metadata?
    def __init__(self, args, body: List[Clause], scope):
        # to support multiple bodies - soft intern a relation, then make an exploder
        # maybe something to uniquify them....like a class relationship? yeah...
        # instead of just dumping them in a bucket and not being able to talk
        # about them individually
        self.body = body
        self.scope = scope
        self.error = lambda *x :print("errorz", *x)
        super().__init__()

    # ok, we dont really need to dynamize this, we've already deferred signature
    # generation until the query, so we think that it all should be bound
    #
    # change this to generate a list of clauses and move rule out
    def relation_out(self, rel:str, b:ArgSet, next:Construct, args:List[Variable]) -> Stream:
        if rel not in self.scope:
            self.error("no such relation", rel);
        r = self.scope[rel]
            
        if len(args) != len(r.arguments):
            self.error("arity mismatch")

        inbound = {}
        outbound = {}
        const = {}

        print ("args", args, r.arguments, b, r)
        for term, target in zip(args, r.arguments):
            if term in b:
                inbound[term] = target
            else:
                if is_constant(term):
                    const[target] = term
                else:
                    outbound[term] = target

        function = r.signature(frozenset(inbound.values()))
        down = next(b.union(frozenset(outbound.values())))
                    
        def inh(f:Frame):
            save = f["__next__"]
            def outh(outf:Frame):
                f2 = f.copy()
                for output in outbound:
                    f2[output] = outf[outbound[output]]
                f2["__next__"] = save                    
                down(f2)

            input_args = const.copy()
            for input in inbound:
                input_args[inbound[input]] = f[input]
            result = function(input_args, outh)
                
        return inh
        

    def clauses_to_stream(self, body:List[Clause], b:ArgSet, next:Construct) -> Stream:
        i = body.__iter__()
        def each(b:ArgSet) -> Stream:
            print("each", b)
            try:
                statement = i.__next__()
                print("Statement", statement, b)                
                return self.relation_out(statement[0], b, each, statement[1:])
            except StopIteration:
                return next(b)
        return each(b)
    
    # how to get the dynamic next to the tail? we're shoving it in the frame. with a stack
    # to support nesting. not pretty
    def build(self, b:ArgSet) -> RelationStream:
        s = self.clauses_to_stream(self.body, b, lambda b: lambda f: f["__next__"](f))
        def head(f, n):
            f["__next__"] = n 
            s(f)
        return head

