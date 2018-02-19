from functools import singledispatch
from gi.repository import GLib

"""
The function av(arg) (short for auto variant) changes usual data types
to dbus variants. This is especially useful when using pydbus for api calls
which have variants in the signature.
"""

@singledispatch
def av(arg):
    raise NotImplementedError('Unsupported type')

@av.register(int)
def _(arg):
    try:
        return GLib.Variant('i', arg)
    except OverFlowError:
        return GLib.Variant('x', arg)

@av.register(float)
def _(arg):
    return GLib.Variant('d', arg)

@av.register(str)
def _(arg):
    return GLib.Variant('s', arg)

@av.register(bool)
def _(arg):
    return GLib.Variant('b', arg)

@av.register(list)
def _(arg):
    if all(map(lambda x: isinstance(x, str), arg)):
        variant_type = 'as'
    elif all(map(lambda x: isinstance(x, int), arg)):
        variant_type = 'ai'
    elif all(map(lambda x: isinstance(x, float), arg)):
        variant_type = 'ad'
    elif all(map(lambda x: isinstance(x, bool), arg)):
        variant_type = 'ab'
    else:
        arg = [av(a) for a in arg]
        variant_type = 'av'
    return GLib.Variant(variant_type, arg)

@av.register(dict)
def _(arg):
    if all(map(lambda x: isinstance(x, str), arg.keys())):
        variant_type_keys = "s"
    elif all(map(lambda x: isinstance(x, int), arg.keys())):
        variant_type_keys = "i"
    elif all(map(lambda x: isinstance(x, float), arg.keys())):
        variant_type_values = "d"
    elif all(map(lambda x: isinstance(x, bool), arg.keys())):
        variant_type_keys = "b"
    else:
        variant_type_keys = "v"

    if all(map(lambda x: isinstance(x, str), arg.values())):
        variant_type_values = "s"
    elif all(map(lambda x: isinstance(x, int), arg.values())):
        variant_type_values = "i"
    elif all(map(lambda x: isinstance(x, float), arg.values())):
        variant_type_values = "d"
    elif all(map(lambda x: isinstance(x, bool), arg.values())):
        variant_type_values = "b"
    else:
        variant_type_values = "v"

    variant_signature = "a{%s%s}" % (variant_type_keys, variant_type_values)

    ret_args = {}
    for key, value in arg.items():
        if variant_type_keys == "v":
            key = av(key)
        if variant_type_values == "v":
            value = av(value)
        ret_args[key] = value
    return GLib.Variant(variant_signature, ret_args)


