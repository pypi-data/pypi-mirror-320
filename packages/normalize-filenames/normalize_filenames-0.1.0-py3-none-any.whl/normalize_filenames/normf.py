import re
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description='Normalize files')
parser.add_argument("-p", help="Optional Path to normalize.", default=".")

GARBAGE_CHARACTERS = re.compile(r"[\(\)\[\]\$\^\%\#\@\!\"\'\\\s\.,<>]")
CLEAN_DASHES = re.compile(r"-{2,}")

def normalize_path(file_path):
    print(f"Normalizing: {file_path}")
    name = file_path.stem.lower()
    suffix = file_path.suffix
    name = re.sub(GARBAGE_CHARACTERS, "-", name)
    name = re.sub(CLEAN_DASHES, "-", name)
    name = name.strip("-")
    return file_path.replace(file_path.with_name(f"{name}{suffix}"))

def walk_files(initial_path: Path):
    if initial_path.is_dir() and initial_path.anchor != '':
        for p in initial_path.rglob('*'):
            if p.is_dir():
                walk_files(p)
            normalize_path(p)
    elif initial_path.is_file():
        normalize_path(initial_path)
        return

def main():
    args = parser.parse_args()
    path = Path().cwd()
    if args.p:
        path = Path(args.p)
    walk_files(path)


if __name__ == "__main__":
    main()