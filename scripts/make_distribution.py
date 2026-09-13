from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

INCLUDE_PATHS = [
    "CI",
    "CD",
    "src",
    "scripts",
    "tests",
    "experiments",
    "notebooks",
    "config.ini",
    "requirements.txt",
    "Dockerfile",
    "docker-compose.yml",
    "data.dvc",
    "dev_sec_ops.yml",
    "scenario.json",
    ".env.example",
    "README.md",
    "REPORT_LAB1.md",
    "REPORT_LAB2.md",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build distribution zip for lab artifacts")
    parser.add_argument("--lab", default="2", help="Lab number to include in resulting zip file name")
    return parser.parse_args()


def iter_files(base: Path):
    if base.is_file():
        yield base
    else:
        for path in base.rglob("*"):
            if (
                path.is_file()
                and "__pycache__" not in path.parts
                and not path.name.endswith(".pyc")
                and ".pytest_cache" not in path.parts
            ):
                yield path


def main() -> None:
    args = parse_args()
    dist_path = Path(f"dist/lab{args.lab}_distribution.zip")
    dist_path.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(dist_path, "w", compression=ZIP_DEFLATED) as archive:
        for relative in INCLUDE_PATHS:
            root = Path(relative)
            if not root.exists():
                continue
            for file_path in iter_files(root):
                archive.write(file_path, arcname=file_path.as_posix())

    print(f"Distribution created: {dist_path}")


if __name__ == "__main__":
    main()
