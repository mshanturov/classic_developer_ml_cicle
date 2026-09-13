from __future__ import annotations

import configparser
import os
import sys
import unittest

import pandas as pd

sys.path.insert(1, os.path.join(os.getcwd(), "src"))

from preprocess import DataMaker


config = configparser.ConfigParser()
config.read("config.ini")


class TestDataMaker(unittest.TestCase):
    def setUp(self) -> None:
        self.data_maker = DataMaker()

    def test_get_data(self) -> None:
        self.assertTrue(self.data_maker.get_data())

    def test_split_data(self) -> None:
        self.assertTrue(self.data_maker.split_data())

    def test_save_split_data(self) -> None:
        x_data = pd.read_csv(config["DATA"]["x_data"], index_col=0)
        self.assertTrue(self.data_maker.save_split_data(x_data, self.data_maker.x_path))


if __name__ == "__main__":
    unittest.main()
