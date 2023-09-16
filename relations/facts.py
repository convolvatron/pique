from relation import *
from typing import *

# we assume that relations consisting of facts (discrete relations) are disjoint from programatically defined
# relations. under the notion that a relation is a logic or of implementations, this isn't necessary .


# we use the whole tuple as the value under the assumption that
# the storage is shared and it would be actually wasteful to
# remove the redundant columns

# no deletion!

class Facts(Relation):

    # frames should really be lists not dicts
    def index_key(self, keys:ArgSet, f:Frame) -> Tuple:
        lookup = []
        # we use this construction in order to following the ordering in arguments
        # we certainly cant use a set of values
        for i in self.arguments:
            if i in keys:
                lookup.append(f[i])
        return tuple(lookup)

    def index_insert(self, keys, body, f:Frame):
        key = self.index_key(keys, f)
        if key not in body:
            body[key] = []
        print("index insert", key, f)
        body[key].append(f)

    # blowing out all indices ever required is a dismal policy. additional
    # insert overhead and footprint need to be balanced against usage and
    # cardinality
    def build_index(self, keys:ArgSet) ->Stream:
        if keys not in self.indices:
            print ("buildindex", keys)
            ind : Dict[ArgSet, List[Tuple]]= {}
            for i in self.base:
                self.index_insert(keys, ind, i)
                
            def lookup(f:Frame, next:Stream):
                print("lookup", keys, f)
                k = self.index_key(f.keys(), f)
                if k in ind:
                    for i in ind[k]:
                        next(i)
                    
            self.indices[keys] = lookup
        return self.indices[keys]

    #positional, so we're translating from frame..fix
    #incremental with subscriptions:)    
    def insert(self, terms):
        named = {}
        for i, n in enumerate(self.arguments):
            named[n] = terms[i]
        self.base.append(named)

        for k, v in self.indices:
            self.index_insert(k, v, named)
        
    def __init__(self, args):
        # base is a list of all the tuples in this relation, which is redundant
        self.base=[]
        self.indices = {}
        super().__init__(args, signature_cache(self.build_index))
        

    
    
