from ochtendzon.deps.management import *

def update(args):
    return update_dependencies()


def add(args):
    return add_dependency(args.name, args.version, args.src)


def remove(args):
    return remove_dependency(args.name)
