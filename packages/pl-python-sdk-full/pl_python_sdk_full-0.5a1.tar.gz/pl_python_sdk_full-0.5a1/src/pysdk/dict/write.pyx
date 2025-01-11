import list.write
def write_klist(d, sep = " ", end = "\n"):
    list.write.write([k for k, v in d.items()], sep, end)
def write_vlist(d, sep = " ", end = "\n"):
    list.write.write([v for k, v in d.items()], sep, end)
