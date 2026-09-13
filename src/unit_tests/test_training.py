from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(1, os.path.join(os.getcwd(), "src"))

from train import MultiModel


class TestMultiModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.multi_model = MultiModel()

    def test_log_reg(self) -> None:
        self.assertTrue(self.multi_model.log_reg())

    def test_rand_forest(self) -> None:
        self.assertTrue(self.multi_model.rand_forest(use_config=True))

    def test_knn(self) -> None:
        self.assertTrue(self.multi_model.knn(use_config=True))

    def test_svm(self) -> None:
        self.assertTrue(self.multi_model.svm(use_config=True))

    def test_gnb(self) -> None:
        self.assertTrue(self.multi_model.gnb())

    def test_d_tree(self) -> None:
        self.assertTrue(self.multi_model.d_tree(use_config=True))


if __name__ == "__main__":
    unittest.main()
