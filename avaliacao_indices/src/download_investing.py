#%%
import investpy as inv
import json
from pprint import pprint
import time
import os

with open("avaliacao_indices/data/investpy_index.json", "r") as f:
    translate_ticker = json.load(f)

pprint(translate_ticker["traducao"])

# %%
indices = translate_ticker["traducao"]

# %%
for index in indices:
    try:
        if os.path.exists(f"avaliacao_indices/data/prices/{index}.csv"):
            print(f"Arquivo {index} já existe")
            continue
        df = inv.get_index_historical_data(
            index=indices[index],
            country="brazil",
            from_date="01/01/2000",
            to_date="01/10/2025",
            interval="Daily"
        )
        df.to_csv(f"avaliacao_indices/data/prices/{index}.csv")
        print(f"Baixado {index}")
    except Exception as e:
        print(f"Erro ao baixar {index}: {e}")
        continue
    time.sleep(2)

# %%
