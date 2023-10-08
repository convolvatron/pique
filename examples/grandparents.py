
@rule
def grandparent(grandparent, grandchild):
    parent(parent, grandchild)
    parent(grandparent, parent)
    

# parents is a class, not an instance
parent = Facts(['parent', 'child'], 
                facts = [
                    ("joe", "nancy"),
                    ("barbara", "nancy"),    
                    ("susan", "joe"),
                    ("egbert", "joe"),
                    ("nancy", "tommy"),
                    ("egbert", "tyrone"),
                    ("tyrone", "tommy"),
                    ("nancy", "ludmilla")])

query("grandparent", {"grandchild":"tommy"}, print)
          
