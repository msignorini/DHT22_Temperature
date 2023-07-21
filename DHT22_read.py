import math
import time
import boto3
import json
import logging
import Adafruit_DHT
from decimal import Decimal
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Configure logging
filename = "log.txt"

# Avoid printing 628 after 2021-05-25 16:30:30,628
formatter = logging.Formatter(
    fmt='%(asctime)s - %(levelname)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Add a rotating handler, 1MB log file and 10s backups
handler = RotatingFileHandler(filename, maxBytes=1048576, backupCount=10)
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

logger.info("Script begin")

# DHT sensor model
DHT_SENSOR = Adafruit_DHT.DHT22

# GPIO pin number
DHT_PIN = 4

# DynamoDB table name
dynamodbTableName = 'Home_Environment'

# DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodbTableName)

n_read = 5
temp_list = []
hum_list = []

# Get timestamp
timestamp = (datetime.now()).strftime("%Y-%m-%dT%H:%M")

# Read 'n_read' times the parameters
i = 0
while i < n_read:
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

    if humidity is not None and temperature is not None:
        temp_list.append(temperature)
        hum_list.append(humidity)
        i += 1
        print("Read #{0}: Temperature={1:0.1f}*C  Humidity={2:0.1f}%".format(i, temperature, humidity))
    else:
        print('Failed to get reading. Try again!')

    time.sleep(3) # Delay for 3 seconds

# Sort both lists
temp_list.sort()
hum_list.sort()

# Delete min and max
temp_list = temp_list[1:-1]
hum_list = hum_list[1:-1]

# Calculate average values
temperature = round(sum(temp_list)/len(temp_list), 1)
humidity = round(sum(hum_list)/len(hum_list), 1)

# Print on screen
msg = 'Temperature={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity)
print(msg)
logger.info(msg)

requestBody = {
    "Timestamp": timestamp,
    "Temperature": Decimal(str(temperature)),
    "Humidity": Decimal(str(humidity))
}

# Insert values to DynamoDB
try:
    table.put_item(Item=requestBody)
    print("Values inserted in DynamoDB")
    logger.info("Values inserted in DynamoDB")
except Exception as e:
    print(e)
    logger.error(e)

logger.info("Script end")
