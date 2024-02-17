"""
namespace?

set of fields with names inside? - dont like pad1 pad2 mbz1...etc

structure = {(name, field)}
  field : structure | immediate
  immediate : {
    offset
    default: value if none is specified
    length: number of bits
    encoding [a relation from bitstring to bitstring]
  }

 
"""

def encode_forward(structured) ->Iterable[Relation]:
    pass

def decode(buffer) ->Iterable[Relation]:
    pass

# could add validate
encode = Relation(["value", 0],
                  fixed_handlers(({'value'}, decode),
                                 ({0},       encode_forward)))
                  ):
