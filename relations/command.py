```processes are interesting because they seem like they are inherently causal (procedural).
   we're going to monotonize them by adding a timestamp. we assume they are synchronous
   and run to completion
```
import subprocess
from relation import *
from typing import *

class Command(Relation):
    arguments = ['command', 'input', 'output', 'time']
    def generate_signature(self, ArgSet):
        pass

class CommandStatus(Relation):
    arguments = ['command', 'input', 'output', 'time']
    def generate_signature(self, ArgSet):
        pass
