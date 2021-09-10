import setuptools
import subprocess
from os.path import abspath, dirname, join
from pathlib import Path


def here(rel_path): return join(abspath(dirname(__file__)), rel_path)
def read(rel_path): return Path(here(rel_path)).read_text()


def long_description():
    lines = read('README.md').splitlines()
    lines_ = []
    cut = False
    for line in lines:
        if '<!-- cut -->' in line:
            cut = True
        elif '<!-- end -->' in line:
            cut = False
        elif not cut:
            lines_.append(line)
    return '\n'.join(lines_)


setuptools.setup(
    version=subprocess.check_output([here('describe-version')]).decode('utf-8').strip(),
    long_description=long_description(),
)
