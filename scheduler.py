import schedule
import time
import functions as fn
from entsoe import EntsoePandasClient
#import telegram_bot as tel
from threading import Thread
import global_variables as g

#fn.setupGPIO()

#background_thread = Thread(target=tel.set_tel_bot, args=())
#background_thread.start()

schedule.every().day.at("14:00").do(g.client.rescheduler)
schedule.every().hour.at(":00").do(g.client.controler)

while True:
    schedule.run_pending()
    time.sleep(1)
