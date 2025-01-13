import re
import argparse
from pathlib import Path
from unidecode import unidecode
import emoji

parser = argparse.ArgumentParser(description='Normalize files')
parser.add_argument("-p", help="Optional Path to normalize.", default=".")
parser.add_argument("-v", help="Version number", action="store_true")
parser.add_argument("-e", help="emojis to ascii in your filename. If not set, the emoji will just be stripped. If set, you will get :<EMOJI_NAME>:", action="store_true")

GARBAGE_CHARACTERS = re.compile(r"[()\[\]$^%#@!?\"\'\\\s.,<>&|]")
CLEAN_DASHES = re.compile(r"-{2,}")

args = parser.parse_args()

def ascii_emoji(text):
    return emoji.demojize(text)

def print_version():
    from . import VERSION
    print(VERSION)

def normalize_path(file_path):
    print(f"Normalizing: {file_path}")
    name = file_path.stem.lower()
    suffix = file_path.suffix
    if args.e:
        name = ascii_emoji(name)
    name = unidecode(name)
    name = re.sub(GARBAGE_CHARACTERS, "-", name)
    name = re.sub(CLEAN_DASHES, "-", name)
    name = name.strip("-")
    return file_path.replace(file_path.with_name(f"{name}{suffix}"))

def walk_files(initial_path: Path):
    if initial_path.is_dir():
        for pth in initial_path.rglob('*'):
            if pth.is_dir():
                walk_files(pth)
            normalize_path(pth)
    elif initial_path.is_file():
        normalize_path(initial_path)

def main():
    if args.v:
        print_version()
        return
    path = Path().cwd()
    if args.p:
        path = Path(args.p)
    walk_files(path)


if __name__ == "__main__":
    main()