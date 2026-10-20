import os
from ochtendzon.build.process import transpile_file, compile_file


def build_folder(args, folder, object_files):
  with os.scandir(folder) as it:
    for entry in it:
      if entry.is_file() and entry.name.endswith('.tau'): build_file(args, entry.path, object_files)
      elif entry.is_dir(): build_folder(args, entry.path, object_files)


def build_file(args, file, object_files: list[str]):
  output = os.path.dirname(file).replace('src', 'target', 1)
  create_folder(output)

  transpile_file(file, output, args.target)

  base, _ = os.path.splitext(file.replace('src', 'target'))
  compile_file(base)
  
  object_files.append(f'{base}.o')

  
def create_folder(folder):
  os.makedirs(folder, exist_ok=True)
