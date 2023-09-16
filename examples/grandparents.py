

facts = [
    ("parent", "joe", "nancy"),
    ("parent", "barbara", "nancy"),    
    ("parent", "susan", "joe"),
    ("parent", "egbert", "joe"),
    ("parent", "nancy", "tommy"),
    ("parent", "egbert", "tyrone"),
    ("parent", "tyrone", "tommy"),
    ("parent", "nancy", "ludmilla")]

@rule
def grandparent(grandparent, grandchild):
    parent(parent, grandchild)
    parent(grandparent, parent)
    
relation("parent", ["parent", "child"])
query(facts, "grandparent", {"grandchild":"tommy"}, print)
          
