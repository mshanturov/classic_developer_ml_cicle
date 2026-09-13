from __future__ import annotations

import argparse
import configparser
import os
import pickle
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from logger import Logger

SHOW_LOG = True


class MultiModel:
    """Trains several classic ML models for seeds classification."""

    def __init__(self) -> None:
        logger = Logger(SHOW_LOG)
        self.log = logger.get_logger(__name__)
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

        self.x_train = pd.read_csv(self.config["SPLIT_DATA"]["x_train"], index_col=0)
        self.y_train = pd.read_csv(self.config["SPLIT_DATA"]["y_train"], index_col=0).iloc[:, 0]
        self.x_test = pd.read_csv(self.config["SPLIT_DATA"]["x_test"], index_col=0)
        self.y_test = pd.read_csv(self.config["SPLIT_DATA"]["y_test"], index_col=0).iloc[:, 0]

        self.scaler = StandardScaler()
        self.x_train = self.scaler.fit_transform(self.x_train)
        self.x_test = self.scaler.transform(self.x_test)

        self.experiments_path = Path("experiments")
        self.experiments_path.mkdir(parents=True, exist_ok=True)

        self.model_paths = {
            "LOG_REG": self.experiments_path / "log_reg.sav",
            "RAND_FOREST": self.experiments_path / "rand_forest.sav",
            "KNN": self.experiments_path / "knn.sav",
            "SVM": self.experiments_path / "svm.sav",
            "GNB": self.experiments_path / "gnb.sav",
            "D_TREE": self.experiments_path / "d_tree.sav",
        }
        self.log.info("MultiModel is ready")

    def log_reg(self, predict: bool = False) -> bool:
        classifier = LogisticRegression(max_iter=1000, random_state=42)
        classifier.fit(self.x_train, self.y_train)
        if predict:
            y_pred = classifier.predict(self.x_test)
            print(accuracy_score(self.y_test, y_pred))
        return self.save_model(classifier, "LOG_REG", {"path": str(self.model_paths["LOG_REG"])})

    def rand_forest(self, use_config: bool, n_trees: int = 300, criterion: str = "gini", predict: bool = False) -> bool:
        if use_config:
            n_trees = self.config.getint("RAND_FOREST", "n_estimators")
            criterion = self.config["RAND_FOREST"].get("criterion", "gini")
        classifier = RandomForestClassifier(
            n_estimators=n_trees,
            criterion=criterion,
            max_depth=self.config.getint("RAND_FOREST", "max_depth", fallback=8),
            random_state=self.config.getint("RAND_FOREST", "random_state", fallback=42),
        )
        classifier.fit(self.x_train, self.y_train)
        if predict:
            y_pred = classifier.predict(self.x_test)
            print(accuracy_score(self.y_test, y_pred))
        params = {
            "n_estimators": str(n_trees),
            "criterion": criterion,
            "max_depth": self.config["RAND_FOREST"].get("max_depth", "8"),
            "random_state": self.config["RAND_FOREST"].get("random_state", "42"),
            "path": str(self.model_paths["RAND_FOREST"]),
        }
        return self.save_model(classifier, "RAND_FOREST", params)

    def knn(self, use_config: bool, n_neighbors: int = 5, metric: str = "minkowski", p: int = 2, predict: bool = False) -> bool:
        if use_config:
            n_neighbors = self.config.getint("KNN", "n_neighbors")
            metric = self.config["KNN"].get("metric", "minkowski")
            p = self.config.getint("KNN", "p")
        classifier = KNeighborsClassifier(n_neighbors=n_neighbors, metric=metric, p=p)
        classifier.fit(self.x_train, self.y_train)
        if predict:
            y_pred = classifier.predict(self.x_test)
            print(accuracy_score(self.y_test, y_pred))
        params = {
            "n_neighbors": str(n_neighbors),
            "metric": metric,
            "p": str(p),
            "path": str(self.model_paths["KNN"]),
        }
        return self.save_model(classifier, "KNN", params)

    def svm(self, use_config: bool, kernel: str = "rbf", random_state: int = 42, predict: bool = False) -> bool:
        if use_config:
            kernel = self.config["SVM"].get("kernel", "rbf")
            random_state = self.config.getint("SVM", "random_state")
        classifier = SVC(kernel=kernel, random_state=random_state)
        classifier.fit(self.x_train, self.y_train)
        if predict:
            y_pred = classifier.predict(self.x_test)
            print(accuracy_score(self.y_test, y_pred))
        params = {
            "kernel": kernel,
            "random_state": str(random_state),
            "path": str(self.model_paths["SVM"]),
        }
        return self.save_model(classifier, "SVM", params)

    def gnb(self, predict: bool = False) -> bool:
        classifier = GaussianNB()
        classifier.fit(self.x_train, self.y_train)
        if predict:
            y_pred = classifier.predict(self.x_test)
            print(accuracy_score(self.y_test, y_pred))
        return self.save_model(classifier, "GNB", {"path": str(self.model_paths["GNB"])})

    def d_tree(self, use_config: bool, criterion: str = "gini", predict: bool = False) -> bool:
        if use_config:
            criterion = self.config["D_TREE"].get("criterion", "gini")
        classifier = DecisionTreeClassifier(criterion=criterion, random_state=42)
        classifier.fit(self.x_train, self.y_train)
        if predict:
            y_pred = classifier.predict(self.x_test)
            print(accuracy_score(self.y_test, y_pred))
        params = {
            "criterion": criterion,
            "path": str(self.model_paths["D_TREE"]),
        }
        return self.save_model(classifier, "D_TREE", params)

    def save_model(self, classifier: object, name: str, params: dict[str, str]) -> bool:
        output_path = Path(params["path"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("wb") as file:
            pickle.dump(classifier, file)

        self.config[name] = params
        with open("config.ini", "w", encoding="utf-8") as config_file:
            self.config.write(config_file)

        self.log.info("Saved model %s to %s", name, output_path)
        return output_path.exists()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train classic ML models for Wheat Seeds")
    parser.add_argument(
        "--model",
        choices=["ALL", "LOG_REG", "RAND_FOREST", "KNN", "SVM", "GNB", "D_TREE"],
        default="ALL",
    )
    parser.add_argument("--use-config", action="store_true")
    parser.add_argument("--predict", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    model = MultiModel()

    if args.model == "ALL":
        model.log_reg(predict=args.predict)
        model.rand_forest(use_config=args.use_config, predict=args.predict)
        model.knn(use_config=args.use_config, predict=args.predict)
        model.svm(use_config=args.use_config, predict=args.predict)
        model.gnb(predict=args.predict)
        model.d_tree(use_config=args.use_config, predict=args.predict)
        return

    if args.model == "LOG_REG":
        model.log_reg(predict=args.predict)
    elif args.model == "RAND_FOREST":
        model.rand_forest(use_config=args.use_config, predict=args.predict)
    elif args.model == "KNN":
        model.knn(use_config=args.use_config, predict=args.predict)
    elif args.model == "SVM":
        model.svm(use_config=args.use_config, predict=args.predict)
    elif args.model == "GNB":
        model.gnb(predict=args.predict)
    elif args.model == "D_TREE":
        model.d_tree(use_config=args.use_config, predict=args.predict)


if __name__ == "__main__":
    main()
