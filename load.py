#!python3

import ast
import sys
import pathlib
import translate
from relation import *

import relations.map
import relations.filesystem
import relations.facts
import relations.rule

def error(*args):
    print(*args)
    sys.exit(-1)    

def is_rule(f: ast.FunctionDef) -> bool:
    for d in f.decorator_list:
        if d.id == "rule":
            return True
    return False

def is_facts(f: ast.ClassDef) -> bool:
    for b in f.bases:
        if b.id == "Facts":
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
        if isinstance(i, ast.FunctionDef) and is_rule(i):
            # move to translate
            clauses = t.body_to_clauses(i.body)
            # should carry metadata too
            print(clauses)
            names = map(lambda a: a.arg, i.args.args)
            print("args", names)
            mod.__dict__[i.name] = relations.rule.Rule(translate.listmap(names),
                                                       clauses,
                                                       mod.__dict__)
            continue
        
        filtered.append(i)

        #    qp = ast.parse(_query_text, filename, mode='exec')
        #    filtered.append(qp.body[0])
    mod.body = filtered
    qm = compile(mod, filename, "exec")

    local = mod.__dict__
    def query(relname, locals, handler):
        # dot syntax
        if relname not in local:
            error("no relation", relname)
        rel = local[relname]
        frame = {"locals":locals, "next":handler, "flush":True}
        s = rel.signature(frozenset(locals.keys()))
        print ("exec", s)
        s(frame, print)
     
    # i dont know why...I insist on making Facts implcitly included..so think about that
    local["Facts"] = relations.facts.Facts
    local["query"] = query
    exec(qm, local)
        
if __name__ == "__main__":
    text = pathlib.Path(sys.argv[1]).read_text()
    # this is..quite sad, but trying to get this stapled on at the ast level
    # violates some fussy namespace construction in ast.parse. the parse/compile/exec
    # boundry is pretty poorly defined
    translate_file(sys.argv[1], text)
