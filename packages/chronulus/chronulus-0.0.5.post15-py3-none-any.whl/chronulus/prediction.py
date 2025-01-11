import pandas as pd


class Prediction:

    def __init__(self, _id: str, text: str, df: pd.DataFrame):
        self.id = _id
        self.text = text
        self.df = df
