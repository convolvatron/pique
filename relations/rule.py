from typing import *
from relation import *

# rule should really be a separate layer than ast translation
# we originally passed around our own namespace - and decided to use pythons
Construct = Callable[[ArgSet], List[Clause]]

class Rule(Relation):
    # what about heads?
    def __init__(self, args, body: List[Clauses], scope):
        # to support multiple bodies - soft intern a relation, then make an exploder
        # maybe something to uniquify them....like a class relationship? yeah...
        # instead of just dumping them in a bucket and not being able to talk
        # about them individually
        self.body = body
        self.scope = scope
        self.filename = filename


    # ok, we dont really need to dynamize this, we've already deferred signature
    # generation until the query, so we think that it all should be bound
    #
    # change this to generate a list of clauses and move rule out
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
        
    # name, args, body, returns, type_comment
    def generate_signature(self, b:ArgSet) -> RelationStream:
        t = Translate(self.filename, sel.scope, print)
        return t.generate(self.body, b)

    def clauses_to_stream(self, body:List[Clause], b:ArgSet, next:Construct) -> Stream:
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
