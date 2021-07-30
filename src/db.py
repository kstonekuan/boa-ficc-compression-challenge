import pandas as pd
import numpy as np

class DB:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path

    def load(self, filename):
        return pd.read_csv(f'{self.input_path}/{filename}').dropna(axis=1)

    def save(self, df, filename):
        df.to_csv(f'{self.output_path}/{filename}', index=False)