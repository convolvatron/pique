"""this shouldn't be needed for many (all?) cases - names should be gathered into equivalence classes by the compiler, but since we're quick and dirty today"""

class Equals(Relation):
    generate_signature: fixed_handlers(({'value', 0, 1}, one_way),
                                       ({0, 1},          other_way)))
