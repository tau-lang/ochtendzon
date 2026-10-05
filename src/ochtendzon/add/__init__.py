from ochtendzon.deps import add_dependency

def add(args):
    return add_dependency(args.name, args.version, args.src)
