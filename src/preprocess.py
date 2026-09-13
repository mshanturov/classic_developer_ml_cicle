from __future__ import annotations

import configparser
import os
from pathlib import Path
from urllib.request import urlretrieve

import pandas as pd
from sklearn.model_selection import train_test_split

from logger import Logger

SHOW_LOG = True
TEST_SIZE = 0.2
RANDOM_STATE = 42
DATA_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00236/seeds_dataset.txt"
COLUMNS = [
    "area",
    "perimeter",
    "compactness",
    "kernel_length",
    "kernel_width",
    "asymmetry_coefficient",
    "groove_length",
    "class",
]


class DataMaker:
    """Loads raw dataset, builds feature/target files, and splits train/test."""

    def __init__(self) -> None:
        logger = Logger(SHOW_LOG)
        self.log = logger.get_logger(__name__)
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

        self.project_path = Path(os.getcwd()) / "data"
        self.raw_path = Path(self.config.get("DATA", "raw_data", fallback=str(self.project_path / "seeds_dataset.txt")))
        self.x_path = Path(self.config.get("DATA", "x_data", fallback=str(self.project_path / "Seeds_X.csv")))
        self.y_path = Path(self.config.get("DATA", "y_data", fallback=str(self.project_path / "Seeds_y.csv")))

        self.train_x_path = Path(self.config.get("SPLIT_DATA", "x_train", fallback=str(self.project_path / "Train_Seeds_X.csv")))
        self.train_y_path = Path(self.config.get("SPLIT_DATA", "y_train", fallback=str(self.project_path / "Train_Seeds_y.csv")))
        self.test_x_path = Path(self.config.get("SPLIT_DATA", "x_test", fallback=str(self.project_path / "Test_Seeds_X.csv")))
        self.test_y_path = Path(self.config.get("SPLIT_DATA", "y_test", fallback=str(self.project_path / "Test_Seeds_y.csv")))

        self.project_path.mkdir(parents=True, exist_ok=True)
        self.log.info("DataMaker is ready")

    def download_raw_data(self) -> bool:
        if self.raw_path.exists():
            self.log.info("Raw dataset already exists")
            return True
        urlretrieve(DATA_URL, self.raw_path)
        self.log.info("Raw dataset downloaded")
        return self.raw_path.exists()

    def get_data(self) -> bool:
        self.download_raw_data()
        dataset = pd.read_csv(self.raw_path, sep=r"\s+", header=None)
        dataset.columns = COLUMNS

        x_data = dataset[COLUMNS[:-1]]
        y_data = dataset[["class"]]

        x_data.to_csv(self.x_path, index=True)
        y_data.to_csv(self.y_path, index=True)

        self.config["DATA"] = {
            "raw_data": str(self.raw_path),
            "x_data": str(self.x_path),
            "y_data": str(self.y_path),
        }
        with open("config.ini", "w", encoding="utf-8") as config_file:
            self.config.write(config_file)

        is_ready = self.x_path.exists() and self.y_path.exists()
        if is_ready:
            self.log.info("X and y data are ready")
        else:
            self.log.error("X and y data were not created")
        return is_ready

    def split_data(self, test_size: float = TEST_SIZE, random_state: int = RANDOM_STATE) -> bool:
        self.get_data()

        x_data = pd.read_csv(self.x_path, index_col=0)
        y_data = pd.read_csv(self.y_path, index_col=0)

        x_train, x_test, y_train, y_test = train_test_split(
            x_data,
            y_data,
            test_size=test_size,
            random_state=random_state,
            stratify=y_data,
        )

        self.save_split_data(x_train, self.train_x_path)
        self.save_split_data(y_train, self.train_y_path)
        self.save_split_data(x_test, self.test_x_path)
        self.save_split_data(y_test, self.test_y_path)

        self.config["SPLIT_DATA"] = {
            "x_train": str(self.train_x_path),
            "y_train": str(self.train_y_path),
            "x_test": str(self.test_x_path),
            "y_test": str(self.test_y_path),
        }
        with open("config.ini", "w", encoding="utf-8") as config_file:
            self.config.write(config_file)

        is_ready = all(
            path.exists()
            for path in [self.train_x_path, self.train_y_path, self.test_x_path, self.test_y_path]
        )
        if is_ready:
            self.log.info("Train and test data are ready")
        return is_ready

    def save_split_data(self, dataframe: pd.DataFrame, path: Path) -> bool:
        dataframe.reset_index(drop=True).to_csv(path, index=True)
        self.log.info("Saved %s", path)
        return path.exists()


if __name__ == "__main__":
    data_maker = DataMaker()
    data_maker.split_data()
