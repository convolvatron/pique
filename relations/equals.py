# this shouldn't be needed for many (all?) cases - names should be gathered into equivalence classes by the compiler

from relation import *
from typing import *

relation = Relation([0,1],
                    # there are more here         
                    fixed_handlers(({'value', 0, 1}, one_way),
                                   ({0, 1},          other_way)))
