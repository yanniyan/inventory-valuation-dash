import pandas as pd

df = pd.read_csv("data/inventory_valuation_12m.csv")
print(df.columns)
print(df.dtypes)
print(df.head())
