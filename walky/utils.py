def object_method_prevent_rpc(f):
    f._norpc = True
    return f


