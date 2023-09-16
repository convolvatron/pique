#!/usr/local/bin/python3

import ast
import sys
import pathlib
import translate
from relation import *

import relations.map
import relations.filesystem
import relations.facts

def error(*args):
    print(*args)
    sys.exit(-1)    

def is_rule(f: ast.FunctionDef) -> bool:
    for d in f.decorator_list:
        if d.id == "rule":
            return True
    return False

    

def translate_file(filename, text, rels:Dict[str, Relation]):
    mod = ast.parse(text, filename=sys.argv[1], mode='exec', type_comments=False)
    t = translate.Translate(sys.argv[1], rels, error)
    filtered = []
    for i in mod.body:
        if isinstance(i, ast.FunctionDef) and is_rule(i):
            rels[i.name] = translate.Rule(i, filename, rels)
        else:
            filtered.append(i)
    mod.body = filtered
    qm = compile(mod, filename, "exec")
    
    def query(facts, relname, frame, handler):
        for i in facts:
            if i[0] not in rels:
                error("no relation", i[0])
            rel = rels[i[0]] 
            # check to insure this is a fact relation
            rel.insert(i[1:])

        if relname not in rels:
            error("no relation", relname)
        rel = rels[relname]

        s = rel.generate_signature(frozenset(frame.keys()))
        print ("exec", s)
        s(frame, print)
                
    # create a new fact relation
    def rel(name, args):
        rels[name] = relations.facts.Facts(args)
            
    exec(qm, {"query":query, "relation": rel})
        
if __name__ == "__main__":
    rels = {}
    rels["map"] = relations.map.relation
    text = pathlib.Path(sys.argv[1]).read_text()
    translate_file(sys.argv[1], text, rels)

        
