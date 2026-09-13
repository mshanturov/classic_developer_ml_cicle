from __future__ import annotations

from pathlib import Path
from urllib.request import urlretrieve

DATA_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00236/seeds_dataset.txt"
OUTPUT_PATH = Path("data/raw/seeds_dataset.txt")


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    urlretrieve(DATA_URL, OUTPUT_PATH)
    print(f"Dataset downloaded to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
