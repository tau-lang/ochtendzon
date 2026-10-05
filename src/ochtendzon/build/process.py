import subprocess
import logging

logger = logging.getLogger(__name__)

def transpile_file(input, output, target):
  try:
    process = subprocess.Popen([
      'tau',
      '--input', input,
      '--output', output,
      '--target', target,
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
      logger.error(f"When transpiling {input}: {stderr}")
  except FileNotFoundError:
    logger.error("Could not find tau compiler")


def compile_file(base):
  try:
    process = subprocess.Popen([
      'g++',
      '-c', f'{base}.cpp', 
      '-o', f'{base}.o'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
      logger.error(f"When compiling {base}.cpp: {stderr}")
  except FileNotFoundError:
    logger.error("Could not find c++ compiler")


def link_binary(output, object_files):
  try:
    args = ['g++', '-o', output]
    args.extend(object_files)
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()

    # Print the return code (0 means success)
    if process.returncode != 0:
      logger.error(f"When linking {output}: {stderr}")
  except FileNotFoundError:
    logger.error("Could not find c++ linker")
