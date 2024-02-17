from relation import *
from typing import *

class Union(Relation):
    def __init__(args):
        self.args = args
        self.children = []

    def signature(self, b :ArgSet) -> Stream:
        cs = map(lambda c: c.signature(b), self.children)
        # we dont really need the results here
        # we need to join the flushes
        return lambda f: map(lambda s:s(f), cs)

    def insert(r:Relation):
        i.children.append(r)
        
        
        
