import logging

def main():
  import os
  import argparse

  parser = argparse.ArgumentParser(
    prog='ochtendzon',
    description='Simple compiler toolchain for the Tau language. ',
    fromfile_prefix_chars='@',
    suggest_on_error=True,
  )

  subparsers = parser.add_subparsers(title='commands', required=True, dest='command')

  parser_build = subparsers.add_parser('build', help='Compile the current package')
  parser_build.add_argument('--target', choices=('cpp', 'cranelift'), default='cpp')

  parser_init = subparsers.add_parser('init', help='Create a new ochtendzon package')
  parser_init.add_argument('--name', type=str)
  parser_init.add_argument('-f', '--force', action='store_true')

  parser_run = subparsers.add_parser('run', help='Run a binary of the local package')

  parser_add = subparsers.add_parser('add', help='Add the package to the dependencies')
  parser_add.add_argument('name', nargs='?', type=str)
  parser_add.add_argument('version', nargs='?', type=str)
  parser_add.add_argument('src', nargs='?', type=str)

  parser_update = subparsers.add_parser('update', help='Updates all dependencies')

  parser_remove = subparsers.add_parser('remove', help='Remove the package from the dependencies')
  parser_remove.add_argument('name', nargs='?', type=str)

  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

  match args.command:
    case 'build':
      from ochtendzon.build import build
      return build(args)

    case 'init':
      from ochtendzon.init import init
      return init(args)

    case 'run':
      from ochtendzon.build import build
      status = build(parser_build.parse_args([]))
      if status not in (0, None): return status

      from ochtendzon.run import run
      return run(args)

    case 'add':
      from ochtendzon.deps import add
      return add(args)

    case 'update':
      from ochtendzon.deps import update
      return update(args)

    case 'remove':
      from ochtendzon.deps import remove
      return remove(args)
