import pandas as pd
import datetime
import time
from entsoe import EntsoePandasClient
#import RPi.GPIO as GPIO
import sys


class entsoe_client:
    def __init__(self, default_heating_time = 4, api_key = None) -> None:
        self.client = EntsoePandasClient(api_key = api_key)
        self.default_heating_time = default_heating_time
        self.heating_cycle = 0
        self.rescheduler()
        self.controler()

    def get_rates(self):
        today=datetime.date.today()
        tomorrow =  today + datetime.timedelta(days=2)
        start = pd.Timestamp(today.strftime('%Y%m%d'), tz="Europe/Riga")
        end = pd.Timestamp(tomorrow.strftime('%Y%m%d'), tz="Europe/Riga")
        country_code = 'LV' 
        prices = self.client.query_day_ahead_prices(country_code, start=start,end=end)
        average_hourly_prices = prices.resample('1h').mean()
        return average_hourly_prices
        
    def rescheduler(self):
        prices = self.get_rates()
        d = datetime.datetime.today()+ datetime.timedelta(days=1)
        t = datetime.time(6)
        until_tommorow = datetime.datetime.combine(d, t).strftime('%Y-%m-%d %H')
        now = datetime.datetime.today().strftime('%Y-%m-%d %H')

        try:
            remaining_heating_hours = self.heating_cycle.loc[now:until_tommorow].shape[0]
        except:
            remaining_heating_hours = self.default_heating_time

        a : pd.DataFrame = prices.loc[now:until_tommorow]
        a = a.sort_values().head(remaining_heating_hours)

        b : pd.DataFrame = prices.loc[until_tommorow:]
        b = b.sort_values().head(self.default_heating_time)

        self.heating_cycle = pd.concat([a,b])
        self.heating_cycle = self.heating_cycle.sort_index()
        print("Rescheduling heating hours")
        sys.stdout.flush()
        print(self.heating_cycle)
        sys.stdout.flush()

    def controler(self):
        now = datetime.datetime.today().strftime('%Y-%m-%d %H')  
        current_task : pd.DataFrame = self.heating_cycle.loc[now:now]
        if current_task.shape[0] == 0:
            #GPIO.output(18, GPIO.LOW)
            print("Boiller is off")
            sys.stdout.flush()
        else:
            self.heating_cycle : pd.DataFrame = pd.concat([self.heating_cycle,current_task]).drop_duplicates(keep=False)
            #GPIO.output(18, GPIO.HIGH)
            print("Boiller is on")
            sys.stdout.flush()
            print("Remaining heating hours")
            sys.stdout.flush()
            print(self.heating_cycle)
            sys.stdout.flush()

    def add_aditional(self, time):
        d = datetime.datetime.today()+ datetime.timedelta(days=1)
        t = datetime.time(6)
        until_tommorow = datetime.datetime.combine(d, t).strftime('%Y-%m-%d %H')
        now = datetime.datetime.today().strftime('%Y-%m-%d %H')
        prices = self.get_rates()
        a = prices.loc[now:until_tommorow]
        a = a.sort_index().head(time)

        b = prices.loc[until_tommorow:]
        b = b.sort_values().head(self.default_heating_time)

        self.heating_cycle = pd.concat([a,b])
        self.heating_cycle = self.heating_cycle.sort_index()

        print("Heating cycle after reschedule")
        sys.stdout.flush()
        print(self.heating_cycle)
        sys.stdout.flush()

"""
def setupGPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(18, GPIO.OUT)
    GPIO.output(18, GPIO.LOW)
"""