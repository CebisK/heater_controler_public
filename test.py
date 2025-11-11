#%%
import functions as fn
from entsoe import EntsoePandasClient
from threading import Thread
import global_variables as g
import pandas as pd
#%%
prices :pd.DataFrame = g.client.get_rates()
print(prices)
#%%
prices_copy : pd.DataFrame = prices.copy()
prices_copy["hourly price"] = prices_copy.groupby(prices_copy.index.floor('h'))["prices"].transform('mean')
print(prices_copy)
#%%

