#%%
import functions as fn
from entsoe import EntsoePandasClient
from threading import Thread
import global_variables as g
import pandas as pd
#%%
import datetime

prices :pd.DataFrame = g.client.get_rates()
now = (datetime.datetime.today() + datetime.timedelta(minutes=6)).strftime('%Y-%m-%d %H:%M')
now_offset_14min =  (datetime.datetime.today() - datetime.timedelta(minutes=8)).strftime('%Y-%m-%d %H:%M')
current_task : pd.DataFrame = prices[now_offset_14min:now]
print(current_task)
#%%
g.client.rescheduler()
#%%

