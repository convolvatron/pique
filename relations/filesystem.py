"""in unix filesystems, paths aren't canonical. fsid/inode pairs are. but its 
   a paint to get at them. children is a map, although its maybe better were 
   it a column. we dont need contents, but i dont want to be too fake. it could
   be lazy"""
import datetime
import typing
import relation
from relation import *
from typing import *


def directory_iterate(f:Frame, s:Stream):
    pass

def file_lookup(f:Frame, s:Stream):
    def file_lookup(f: relation.Frame, out: relation.Stream):  
        path = f['id']
        fd = sys.Open(pathname(path), mode="r")
        s({'size':os.path.getsize(path),
        'time': os.path.getmtime(path),
        'contents':""})

def file_scan(f:Frame, s:Stream):
    pass

class File(Relation):
    fixed_handlers(({'file'}, file_lookup),
                   ({}, file_scan))
    arguments = ['path', 'size', 'time', 'contents']
            
class Directory(Relation):
    fixed_handlers(({'id'}, directory_iterate)),
    arguments = ['path', 'child']
