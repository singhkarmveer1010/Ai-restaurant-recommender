import os
import pandas as pd
from datasets import load_dataset

print("Downloading dataset...")
os.makedirs('data', exist_ok=True)
ds = load_dataset('ManikaSaini/zomato-restaurant-recommendation', split='train')
df = ds.to_pandas()
print("Saving as parquet...")
df.to_parquet('data/restaurent.parquest')
print("Done!")
