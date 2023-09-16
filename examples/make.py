"""
section{make - interacting with stateful systems}{
  the little langauge we defined is, at least by intent, pure. Purity, or referential transparency means that
  any evaluation will always return the same result, precluding the use of of hidden state. This makes
  reasonaing about the code much easier. Unfortunately for purity, most uses of a computer are explicitly
  about hidden state
  
  list{
     item{of the user, clearly not under our control}
     item{stored on persistent media}
     item{other programs running on our system, including the kernel}
     item{other systems across the network}
     item{hardware devices attached to our system}
   }

   There are a couple approaches to maintaining purity and still being
   able to interact usefully with the outside world. The first is an enclosing model, where we
   pass some variable, call it code{world}, through all of our functions, and pass it back on completion.

   The approach we're going to take is the eversion of this. The pure 'core' sits inside a driver shell that
   iteracts with the external world, and pushes changes in state by assertion of new facts.
   
   This model works really well with incremental evaluation
}
"""

# we could do tuples instead of applications
# alot of these can be made into rules
facts = [depends("foo.c", "foo.h"),
         depends("foo", "foo.o"),
  	 depends("foo.o", "foo.c")         
         ]

@rule
def update(a):
    d = dependency(a)
    if d.mtime > a.mtime:
        build(a)

@rule
def build(a):
    endswith(a, ".c")
    command("cc {a} -c")
    
@rule
def build(a):
    a == "foo"
    command("cc foo.o -o foo")    
    
@rule
def check(a):
    depends(a, b)
