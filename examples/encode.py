
@rule
def field(t:Template, v:Value) -> Bits
    pass


# keep this in set o bits and union at the end
@rule        
def encode(s:Structure, v:Value) -> Bits:
    template = s[v[v0]]
    return shift_left(encode(field, v0), template.offset)
