import sys


def create_format(start: str, end: str = "\033[0m"):
    # prevents coloring stdout when piped.
    if not sys.stdout.isatty(): (start, end) = ('', '')
    def format(text: str): return start + text + end
    return format

red = create_format("\033[0;31m")
green = create_format("\033[0;32m")
bold = create_format("\033[1m")
yellow = create_format("\033[0;33m")
