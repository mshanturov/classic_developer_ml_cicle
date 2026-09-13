# Converted from notebooks/lab1_experiment.ipynb

import pandas as pd

from src.ml_pipeline.config import ConfigLoader
from src.ml_pipeline.evaluate import ModelEvaluator
from src.ml_pipeline.model import SeedsModelTrainer

config = ConfigLoader("config.ini").load()
trainer = SeedsModelTrainer(config)
evaluator = ModelEvaluator()

train_df = pd.read_csv("data/processed/train.csv")
test_df = pd.read_csv("data/processed/test.csv")

model = trainer.train(train_df)
metrics = evaluator.evaluate(model, test_df)

print(metrics)
