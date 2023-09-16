#!/usr/local/bin/python3
from typing import * 
import sys
import pathlib

#utf8 implications here are problematic at best

def section(context, args):
    d = context["depth"]
    d = d + 1
    
    if d > 6:
        print("nesting depth exceeded")
        sys.exit(-1)
        
    return "\n" + "#"* d + " " + args[0] + "\n" + args[1]


    

def code(context, args):
    return "```"  + args[0] + "```"

# list nesting depth
def list(context, args):
    return args[0]

def item(context, args):
    return "-"  + args[0]

def comment(context, args):
    return ""

def ref(context, args):
    return ""

def urlref(context, args):
    return ""

# can i access the module namespace? __dict__?
github_markdown_handlers = {"section":section,
                            "code":code,
                            "list":list,
                            "item":item,
                            "comment":comment,
                            "ref":ref,
                            "urlref":urlref,
                            }

def whitespace(c:str) -> bool:
    # member is cleaner
    return c == " " or c == "\n"

def block(text:str, start: int, context) ->(int, str):
    last_word = ""
    output = ""
    offset = start

    while offset < len(text):
        c = text[offset]
        if c == "{":
            args = []
            # eat whitespace

            while offset < len(text) and text[offset] == "{" :
                (n, arg) = block(text, offset+1, context)
                offset = n
                args.append(arg)
                
            print("block", last_word, args)                
            output += context["handlers"][last_word](context, args)            
            last_word = ""
            continue
        
        offset = offset+1
        
        if c == "}":
            break
            
        if whitespace(c):
            output += last_word
            output += " "
            last_word = ""
        else:
            # offset management is unpleasant
            last_word += c
        
    return (offset, output)
            


if __name__ == "__main__":
    text = pathlib.Path(sys.argv[1]).read_text()
    (off, res) = block(text, 0, {"handlers":github_markdown_handlers, "depth":0})
    f = open(sys.argv[2], "w")
    f.write(res)
    f.close()
    


        
