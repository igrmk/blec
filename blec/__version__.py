import sys
from os.path import join

if sys.version_info < (3, 8):
    from importlib_metadata import distribution, PackageNotFoundError
else:
    from importlib.metadata import distribution, PackageNotFoundError


def _get_version():
    fallback = '0.0.0.dev0'
    try:
        dist = distribution(__package__)
    except PackageNotFoundError:
        return fallback

    inst_loc = str(dist.locate_file(join(__package__, '__version__.py')))
    return dist.version if inst_loc == __file__ else fallback


__version__ = _get_version()
