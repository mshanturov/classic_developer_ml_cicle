from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

DIST_PATH = Path("dist/lab1_distribution.zip")
INCLUDE_PATHS = [
    "src",
    "scripts",
    "tests",
    "notebooks",
    ".github/workflows",
    "config.ini",
    "requirements.txt",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.dev.yml",
    "dvc.yaml",
    "dev_sec_ops.yml",
    "scenario.json",
    "README.md",
    "REPORT_LAB1.md",
]


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
    DIST_PATH.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(DIST_PATH, "w", compression=ZIP_DEFLATED) as archive:
        for relative in INCLUDE_PATHS:
            root = Path(relative)
            for file_path in iter_files(root):
                archive.write(file_path, arcname=file_path.as_posix())

    print(f"Distribution created: {DIST_PATH}")


if __name__ == "__main__":
    main()
