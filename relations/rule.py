from typing import *
from relation import *

Construct = Callable[[ArgSet], List[Clause]]

def union(*args):
    return args[0].union(*args[1:])

def dunion(*args):
    result = {}
    for i in args:
        print ("dunion args", i)
        for k in i:
            result[k]= i[k]
    return result

class Rule(Relation):
    # this is really an insert?
    def __init__(self, args:ArgSet, body: List[Clause], scope:Dict[Name, Relation]):
        self.body = body
        self.scope = scope
        self.args = args
        super().__init__()

    def call(self, rel:str, bound:ArgSet, next:Construct, args:Dict[Name, Any]) -> Stream:
        # outbound is a map from inner names to outer names
        outbound = {k:v for (k, v) in args.items() if not k in bound}
        down = next(union(bound, outbound.values()))
        def out(oframe):
            print ("oframe", oframe, outbound)
            down(dunion(oframe["parent"]["locals"],
                        {v: oframe[k] for (k, v) in outbound.items()}))
        def inh(f:Frame):
            print ("inh", f)
            # handle free relation? fuse scopes?
            if rel not in self.scope:
                # not really, i guess pass an error handler
                print("no such relation", rel.name.id);
            sig = frozenset({k for k in args.keys() if (args[k] in bound) or is_constant(args[k])})
            function = self.scope[rel].signature(sig)
            # function takes next
            function({"locals":dunion({k:v for (k, v) in args.items() if is_constant(v)},
                                   {k:f["locals"][args[k]] for (k, v) in args.items() if v in bound}),
                      "flush":"flush" in f,
                      "parent":f,
                      "next":out})
        return inh
        
    def clauses_to_stream(self, body:List[Clause], b:ArgSet, next:Construct) -> Stream:
        print ("rule body", body)
        i = body.__iter__()
        # need to collect up all the closure allocations
        def each(b:ArgSet) -> Stream:
            try:
                statement = i.__next__()
                # didn't augment the binding
                return self.call(statement[0], b, each, statement[1])
            except StopIteration:
                return next(b)
        return each(b)

    def build(self, b:ArgSet) -> Stream:
        s = self.clauses_to_stream(self.body, b, lambda b: lambda f: f["next"](f))
        def head(f, n):
            f["next"] = n 
            s(f)
        return head

