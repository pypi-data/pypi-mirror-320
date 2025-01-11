def str_to_list(sep, s):
    return None
def multi_str_to_list(sep, *args):
    ls = []
    for a in args:
        ls.extend(a.split(sep))
    return ls
