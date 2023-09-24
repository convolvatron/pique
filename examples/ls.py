import filesytem
query(facts, "files", {}, lambda a:print(a["id"], a["time"]))
