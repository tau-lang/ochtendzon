import subprocess


def transpile_file(input, output, target):
  process = subprocess.Popen([
    'tau',
    '--input', input,
    '--output', output,
    '--target', target,
  ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
  stdout, stderr = process.communicate()

  if process.returncode != 0:
    print(f"When transpiling {input}: {stderr}")


def compile_file(base):
  process = subprocess.Popen([
    'g++',
    '-c', f'{base}.cpp', 
    '-o', f'{base}.o'
  ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
  stdout, stderr = process.communicate()

  if process.returncode != 0:
    print(f"When compiling {base}.cpp: {stderr}")


def link_binary(output, object_files):
  args = ['g++', '-o', output]
  args.extend(object_files)
  process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
  stdout, stderr = process.communicate()

  # Print the return code (0 means success)
  if process.returncode != 0:
    print(f"When linking {output}: {stderr}")
