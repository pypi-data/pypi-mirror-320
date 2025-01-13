import os
import sys
import argparse
import shutil

from alo.model import settings
from alo.utils import print_copyright
from glo.__version__ import __version__, COPYRIGHT
from glo.rest_api import run


def main():
    parser = argparse.ArgumentParser('GLO', description='GLO(AI Learning Organizer)')
    parser.add_argument('-v', '--version', action='version', version=__version__)
    settings.update()
    print_copyright(COPYRIGHT)
    run(settings.experimental_plan.api)


if __name__ == '__main__':
    main()
