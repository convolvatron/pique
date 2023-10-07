
@rule
def grandparent(grandparent, grandchild):
    parent(parent, grandchild)
    parent(grandparent, parent)
    
class zeg:
    pass
    
class parent:
    arguments = ['parent', 'child']
    facts = [
        ("joe", "nancy"),
        ("barbara", "nancy"),    
        ("susan", "joe"),
        ("egbert", "joe"),
        ("nancy", "tommy"),
        ("egbert", "tyrone"),
        ("tyrone", "tommy"),
        ("nancy", "ludmilla")]

query("grandparent", {"grandchild":"tommy"}, print)
          
