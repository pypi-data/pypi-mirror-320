import list.read
def read_enum(n, s = "", func = lambda s: s):
    ls = list.read.read(n, s, func)
    return {i: ls[i] for i in range(n)}
