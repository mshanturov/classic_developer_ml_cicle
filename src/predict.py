from __future__ import annotations

import argparse
import configparser
from datetime import datetime
import json
import os
from pathlib import Path
import pickle
import shutil
import time

import pandas as pd
from sklearn.preprocessing import StandardScaler
import yaml

from logger import Logger

SHOW_LOG = True
MODEL_CHOICES = ["LOG_REG", "RAND_FOREST", "KNN", "GNB", "SVM", "D_TREE"]


class Predictor:
    """Runs smoke or functional tests for selected trained model."""

    def __init__(self) -> None:
        logger = Logger(SHOW_LOG)
        self.log = logger.get_logger(__name__)

        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

        self.parser = argparse.ArgumentParser(description="Predictor")
        self.parser.add_argument("-m", "--model", type=str, required=True, choices=MODEL_CHOICES)
        self.parser.add_argument("-t", "--tests", type=str, required=True, choices=["smoke", "func"])

        self.x_train = pd.read_csv(self.config["SPLIT_DATA"]["x_train"], index_col=0)
        self.y_train = pd.read_csv(self.config["SPLIT_DATA"]["y_train"], index_col=0).iloc[:, 0]
        self.x_test = pd.read_csv(self.config["SPLIT_DATA"]["x_test"], index_col=0)
        self.y_test = pd.read_csv(self.config["SPLIT_DATA"]["y_test"], index_col=0).iloc[:, 0]

        self.scaler = StandardScaler()
        self.x_train = self.scaler.fit_transform(self.x_train)
        self.x_test = self.scaler.transform(self.x_test)

        self.tests_path = Path(os.getcwd()) / "tests"
        self.exp_path = Path(os.getcwd()) / "experiments"
        self.exp_path.mkdir(parents=True, exist_ok=True)

        self.log.info("Predictor is ready")

    def predict(self) -> bool:
        args = self.parser.parse_args()
        model_path = Path(self.config[args.model]["path"])
        if not model_path.exists():
            raise FileNotFoundError(f"Model file does not exist: {model_path}")

        with model_path.open("rb") as model_file:
            classifier = pickle.load(model_file)

        if args.tests == "smoke":
            score = classifier.score(self.x_test, self.y_test)
            print(f"{args.model} has {score:.4f} score")
            self.log.info("%s passed smoke tests", model_path)
            return True

        test_files = sorted(self.tests_path.glob("test_*.json"))
        if not test_files:
            raise FileNotFoundError("No functional test files found in tests/test_*.json")

        for test_file in test_files:
            with test_file.open("r", encoding="utf-8") as file:
                data = json.load(file)

            x_frame = pd.json_normalize(data, record_path=["X"])
            y_frame = pd.json_normalize(data, record_path=["y"])
            y_series = y_frame.iloc[:, 0]

            x_scaled = self.scaler.transform(x_frame)
            score = classifier.score(x_scaled, y_series)
            print(f"{args.model} has {score:.4f} score for {test_file.name}")
            self.log.info("%s passed func test %s", model_path, test_file.name)

            exp_data = {
                "model": args.model,
                "model_params": dict(self.config.items(args.model)),
                "tests": "func",
                "score": float(score),
                "x_test_path": self.config["SPLIT_DATA"]["x_test"],
                "y_test_path": self.config["SPLIT_DATA"]["y_test"],
            }
            date_time = datetime.fromtimestamp(time.time())
            str_date_time = date_time.strftime("%Y_%m_%d_%H_%M_%S")
            exp_dir = self.exp_path / f"exp_{test_file.stem}_{str_date_time}"
            exp_dir.mkdir(parents=True, exist_ok=True)

            with (exp_dir / "exp_config.yaml").open("w", encoding="utf-8") as exp_file:
                yaml.safe_dump(exp_data, exp_file, sort_keys=False, allow_unicode=True)

            logfile_path = Path(os.getcwd()) / "logfile.log"
            if logfile_path.exists():
                shutil.copy(logfile_path, exp_dir / "exp_logfile.log")
            shutil.copy(model_path, exp_dir / f"exp_{args.model}.sav")

        return True


if __name__ == "__main__":
    predictor = Predictor()
    predictor.predict()
