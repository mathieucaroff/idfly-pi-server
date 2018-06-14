import re

def info(obj):
    typestr = re.sub(r"^<class '(.*)'>$", r"<\1>", repr(type(obj)))
    return "{} {}".format(typestr, repr(obj))

def show(**kwargs):
    """Montre la valeur de la variable renseignée"""
    items = kwargs.items()
    assert len(items) == 1
    key, value = next(iter(items)) # équivalent à items[0]
    printIDFLY("{}:: {}".format(key, info(value))) # f remplace les termes entre crochets par leurs valeurs


def nop(*args, **kwargs):
    pass

def printIDFLY(*arg, **kwargs):
    """Ajoute "[IDFLY]" et affiche les données en paramètre"""
    print("[IDFLY]", *arg, **kwargs)