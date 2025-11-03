import functions as fn
import json

with open('api_keys.json', 'r') as file:
    keys = json.load(file)

client = fn.entsoe_client(4, keys["entso_e"])