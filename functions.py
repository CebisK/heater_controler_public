import pandas as pd
import datetime
import time
from entsoe import EntsoePandasClient
import RPi.GPIO as GPIO
import sys


class entsoe_client:
    def __init__(self, default_heating_time = 4, api_key = None) -> None:
        self.client = EntsoePandasClient(api_key = api_key)
        self.default_heating_time = default_heating_time
        self.heating_cycle = pd.DataFrame()
        self.reschedule_status = False
        self.rescheduler()
        self.controler()


    def get_rates(self):
        today=datetime.date.today()
        tomorrow =  today + datetime.timedelta(days=3)
        start = pd.Timestamp(today.strftime('%Y%m%d'), tz="Europe/Riga")
        end = pd.Timestamp(tomorrow.strftime('%Y%m%d'), tz="Europe/Riga")
        country_code = 'LV' 
        prices : pd.DataFrame = self.client.query_day_ahead_prices(country_code, start=start,end=end).to_frame("prices")
        prices["hourly prices"] = prices.groupby(prices.index.floor('h'))["prices"].transform('mean')
        return prices
        
    def rescheduler(self):
        try:
            prices = self.get_rates()
        except:
            print("Prices not available")
            sys.stdout.flush()
            self.reschedule_status = False
            return
        d = datetime.datetime.today()+ datetime.timedelta(days=1)
        t = datetime.time(7)
        t1 = datetime.time(hour=23)
        t2 = datetime.time(hour=14, minute=15)
        t_evning = datetime.datetime.combine(d, t1).strftime('%Y-%m-%d %H:%M')
        t_auction = datetime.datetime.combine(d, t2).strftime('%Y-%m-%d %H:%M')
        until_tommorow = datetime.datetime.combine(d, t).strftime('%Y-%m-%d %H:%M')
        until_tommorow_excluding = datetime.datetime.combine((d-pd.Timedelta(minutes=15)), t).strftime('%Y-%m-%d %H:%M')
        now = datetime.datetime.today().strftime('%Y-%m-%d %H:%M')
        self.reschedule_status = False

        print("Available prices")
        sys.stdout.flush()
        print(prices)
        sys.stdout.flush()

        try:
            remaining_heating_hours = self.heating_cycle.loc[now:until_tommorow].shape[0]
        except:
            remaining_heating_hours = 0
        
        print("Remaining heating hours")
        sys.stdout.flush()
        print(remaining_heating_hours)
        sys.stdout.flush()

        a : pd.DataFrame = prices.loc[now:until_tommorow_excluding]
        a = a.sort_values(by="hourly prices").head(remaining_heating_hours)

        b : pd.DataFrame = prices.loc[until_tommorow:]

        if b.shape[0] != 0:
            avg_night_price = prices.loc[t_evning:].mean()['prices']
            mask = (b.index <= t_auction) & (b["hourly prices"] > avg_night_price)
            b = b.drop(b[mask].index)
            b = b.sort_values(by="hourly prices").head(self.default_heating_time)

            self.heating_cycle = pd.concat([a,b])
            self.heating_cycle = self.heating_cycle.sort_index()
            print("Rescheduling heating hours")
            sys.stdout.flush()
            print(self.heating_cycle)
            sys.stdout.flush()
            self.reschedule_status = True

    def controler(self):
        if self.reschedule_status == False:
            print("Retraying scheduling")
            sys.stdout.flush()
            self.rescheduler()
            
        now = datetime.datetime.today().strftime('%Y-%m-%d %H:%M')
        now_offset_14min =  (datetime.datetime.today() - datetime.timedelta(minutes=14)).strftime('%Y-%m-%d %H:%M')
        current_task : pd.DataFrame = self.heating_cycle.loc[now_offset_14min:now]
        if current_task.shape[0] == 0:
            GPIO.output(18, GPIO.LOW)
            print("Boiller is off")
            sys.stdout.flush()
        else:
            print(current_task)
            sys.stdout.flush()
            print("Current task^^^^^^^^^^^")
            sys.stdout.flush()
            self.heating_cycle = self.heating_cycle.drop(current_task.index)
            GPIO.output(18, GPIO.HIGH)
            print("Boiller is on")
            sys.stdout.flush()
            print("Remaining heating hours")
            sys.stdout.flush()
            print(self.heating_cycle)
            sys.stdout.flush()

    def add_aditional(self, time):
        d = datetime.datetime.today()+ datetime.timedelta(days=1)
        t = datetime.time(7)
        until_tommorow = datetime.datetime.combine(d, t).strftime('%Y-%m-%d %H:%M')
        until_tommorow_excluding = datetime.datetime.combine((d-pd.Timedelta(minutes=15)), t).strftime('%Y-%m-%d %H:%M')
        now_offset_14min =  (datetime.datetime.today() - datetime.timedelta(minutes=14)).strftime('%Y-%m-%d %H:%M')
        prices = self.get_rates()
        a = prices.loc[now_offset_14min:until_tommorow_excluding]
        a = a.sort_index().head(time)

        b = prices.loc[until_tommorow:]
        b = b.sort_values(by="hourly prices").head(self.default_heating_time)

        self.heating_cycle = pd.concat([a,b])
        self.heating_cycle = self.heating_cycle.sort_index()

        print("Heating cycle after reschedule")
        sys.stdout.flush()
        print(self.heating_cycle)
        sys.stdout.flush()


def setupGPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(18, GPIO.OUT)
    GPIO.output(18, GPIO.LOW)

