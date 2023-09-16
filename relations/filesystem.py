import datetime
import typing
import relation

class Directory:
    children: typing.Dict[str, 'Entry']

# we'd like to build a relation over simple product types, but introspecting
# here is fraught (namespace polluted with internals)
class File:
    mtime: datetime.datetime
    contents: str

Entry = typing.Union[File, Directory]

def pathname(f: Entry) ->str :
    return "/tmp/foo"

def build(a : relation.ArgSet) -> typing.Optional[relation.Stream]:
    return None

def read_contents(f: relation.Frame, out: relation.Stream):
    fd = sys.Open(pathname(f['file']), mode="r")

def Fileystem():
    r = Relation()
    r.generate_signature = build
    r.signatures = {}
    r.arguments: {"name", "contents"}
    return r
    
    
