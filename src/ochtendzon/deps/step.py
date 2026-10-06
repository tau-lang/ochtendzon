import subprocess
import os
import logging

logger = logging.getLogger(__name__)


def run_step(args):
  try:
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
      logger.error(f"When running step {args[0]}: {stderr}")
      return process.returncode
  except FileNotFoundError:
    logger.error(f"Could not find binary: {args[0]}")
    return 1


def find_step(step, name, version, src):
    resolve = f'{name}-{version}'
    cache = os.path.expanduser(f"~/.cache/ochtendzon/deps/{resolve}")
    match step:
        case 'git':
            return run_step([
                'git', 'clone',
                '--recursive',
                '--quiet',
                '--progress',
                '--checkout',
                '--branch', version,
                '--single-branch',
                '--depth', "1",
                src, cache
            ])
        case 'curl':
            os.makedirs(cache, exist_ok = True) 
            download = os.path.join(cache, resolve)
            os.makedirs(cache, exist_ok = True) 
            return run_step([
                'curl', '-s', '-L', src, '-o', download
            ])
        case 'tar':
            download = os.path.join(cache, resolve)
            os.makedirs(cache, exist_ok = True) 
            return run_step([
                'tar', '-xvzf', download, '-C', cache, '--strip-components=1'
            ])
        case _:
            logger.error("Failed to execute {step}, ")
            logger.info("The following steps are known: git, csrc, tar")
            return 1