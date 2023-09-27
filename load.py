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

# we should return a modified class if necessary?
# the original class...also look at __subclasses__ 
def load_facts(c:Type):
    print("start facts", c.name)
    f = relations.facts.Facts(arguments.elts)
    for i in c.facts:
        print("insert", i.elts)
        f.insert(i.elts)
    print("end facts")

def translate_file(filename, text):
    mod = ast.parse(text, filename=sys.argv[1], mode='exec', type_comments=False)
    # there is an oicial way to get module.__dict__?
    t = translate.Translate(sys.argv[1], mod.__dict__, error)
    filtered = []
    for i in mod.body:
        print("stmt", i)
        
        if isinstance(i, ast.FunctionDef) and is_rule(i):
            # tuck this in the namespace
            mod.__dict__[i.name] = translate.Rule(i, filename)            
            continue

        if isinstance (i, ast.Import):
            print("import", i.names)
            for a in i.names:
                print("import", a.name, a.asname)
            continue
        
        filtered.append(i)

    # ok! we can manipulate mod.__dict__
    print("mod dict", mod.__dict__)
    mod.body = filtered
    qm = compile(mod, filename, "exec")
    
    for i in relations.facts.Facts.__subclasses__():
        load_facts(i)
    
    def query(relname, frame, handler):
        if relname not in mod.__dict__:
            error("no relation", relname)
        rel = mod.__dict__[relname]
        s = rel.generate_signature(frozenset(frame.keys()))
        print ("exec", s)
        s(frame, print)

    # i dont know why...I insist on making Facts implcitly included..so think about that 
    exec(qm, {"query":query, "Facts":relations.facts.Facts})
        
if __name__ == "__main__":
    text = pathlib.Path(sys.argv[1]).read_text()
    translate_file(sys.argv[1], text)
