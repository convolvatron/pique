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

# we need to write a section about this class nonsense. its kinda cute, but
# there are edges. in particular we cant really inherit from both

def is_relation(f: ast.ClassDef) -> bool:
    for d in f.bases:
        if d.id == "Relation":
            return True
    return False

def is_fact(f: ast.ClassDef) -> bool:
    for d in f.bases:
        if d.id == "Facts":
            return True
    return False

# we should return a modified class if necessary?
def load_relation(c:ast.ClassDef, rels:RelationSet):
    pass

# we should return a modified class if necessary?
# the original class...also look at __subclasses__ 
def load_facts(c:ast.ClassDef, rels:RelationSet):
    print("start facts", c.name)
    for i in c.body:
        if type(i) == ast.Assign and i.targets[0].id == "facts":
            entries = i.value
        if type(i) == ast.Assign and i.targets[0].id == "arguments":
            arguments = i.value            
    print("foo", c.name, entries, arguments)
    f = relations.facts.Facts(arguments.elts)
    rels[c.name] = f
    for i in entries.elts:
        print("insert", i.elts)
        f.insert(i.elts)
    print("end facts")


def translate_file(filename, text, rels:RelationSet):
    mod = ast.parse(text, filename=sys.argv[1], mode='exec', type_comments=False)
    t = translate.Translate(sys.argv[1], rels, error)
    filtered = []
    for i in mod.body:
        print("stmt", i)
        
        if isinstance(i, ast.FunctionDef) and is_rule(i):
            if i.name not in rels:
                rels[i.name] = []
                rels[i.name] = translate.Rule(i, filename, rels)
            continue
            
        # class ClassDef(name, bases, keywords, body, decorator_list)
        if isinstance(i, ast.ClassDef):
            if is_relation(i):
                load_relation(i)
                continue
            if is_fact(i):
                load_facts(i, rels)
                continue            

        if isinstance (i, ast.Import):
            print("import", i.names)
            for a in i.names:
                print("import", a.name, a.asname)
            continue
        
        filtered.append(i)
        
    mod.body = filtered
    qm = compile(mod, filename, "exec")
    
    def query(relname, frame, handler):
        if relname not in rels:
            error("no relation", relname)
        rel = rels[relname]
        s = rel.generate_signature(frozenset(frame.keys()))
        print ("exec", s)
        s(frame, print)
        
    exec(qm, {"query":query})
        
if __name__ == "__main__":
    rels : Dict[str, List[Relation]] = {}
    text = pathlib.Path(sys.argv[1]).read_text()
    translate_file(sys.argv[1], text, rels)
