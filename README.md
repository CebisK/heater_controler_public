# heater_controler_public
Boiler heating based on entso-e pricing

heater_controller_public
Boiler heating control based on ENTSO-E electricity pricing

# TODO

1. Rename `api_keys_template.json` to `api_keys.json`.  
2. Obtain an ENTSO-E API key and add it to `api_keys.json`.  
   - Guide: [Obtaining an API token from ENTSO-E](https://www.amsleser.no/blog/post/21-obtaining-api-token-from-entso-e)  
3. Create a Telegram bot and generate an access key — to be done. 

# How It Works

1. The system’s goal is to heat the boiler before **06:00** each day.
   The program selects the **cheapest 4 hours** (or however long your boiler needs) to run daily.
2. Every day at **14:00**, the program retrieves **day-ahead prices** from ENTSO-E and:
a. If there are cheaper hours between **00:00–06:00**, it reschedules any remaining heating time.
b. For the next heating cycle, it selects the **lowest-priced hours** between **06:00–24:00**.
3. The **Telegram module** lets you manually switch the boiler on at any time.

# Known Issues

1. The program must be restarted when **daylight saving time** begins or ends.
