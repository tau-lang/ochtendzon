import subprocess
import logging
from ochtendzon.config import env_or_default

logger = logging.getLogger(__name__)

def transpile_file(input, output, target):
  transpiler = env_or_default(['OCHTENDZON_TAU_COMPILER', 'OCHTENDZON_TRANSPILER'], 'tau')
  try:
    process = subprocess.Popen([
      transpiler,
      '--input', input,
      '--output', output,
      '--target', target,
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
      logger.error(f"When transpiling {input}: {stderr}")
  except FileNotFoundError:
    logger.error(f"Could not find tau compiler {transpiler}")


def compile_file(base):
  compiler = env_or_default(['OCHTENDZON_CXX_COMPILER'], 'g++')
  try:
    process = subprocess.Popen([
      compiler,
      '-c', f'{base}.cpp', 
      '-o', f'{base}.o'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
      logger.error(f"When compiling {base}.cpp: {stderr}")
  except FileNotFoundError:
    logger.error(f"Could not find compiler {compiler}")


def link_binary(output, object_files):
  linker = env_or_default(['OCHTENDZON_CXX_LINKER', 'OCHTENDZON_LINKER'], 'g++')
  try:
    args = [linker, '-o', output]
    args.extend(object_files)
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()

    # Print the return code (0 means success)
    if process.returncode != 0:
      logger.error(f"When linking {output}: {stderr}")
  except FileNotFoundError:
    logger.error(f"Could not find linker {linker}")
