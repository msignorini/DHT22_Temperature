import sys
import Adafruit_DHT
import time
import datetime
import csv
import math

# sensor model
sensor = Adafruit_DHT.DHT22
# GPIO pin number
pin = 4
n_read = 5
temp_list = []
hum_list = []

try:
    while True:
        # reset
        i = 0
        temp_list[:] = []
        hum_list[:] = []

        # get timestamp
        st = datetime.datetime.fromtimestamp(time.time())
        tstamp = st.strftime('%Y-%m-%d %H:%M')
        print tstamp

        # read 'n_read' times the parameters
        while i < n_read:
            humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

            if humidity is not None and temperature is not None:
                temp_list.append(temperature)
                hum_list.append(humidity)
                i += 1
                print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
            else:
                print('Failed to get reading. Try again!')
            time.sleep(3) # delay for 3 seconds

        # sort both list
        temp_list.sort()
        hum_list.sort()

        # delete min and max
        temp_list = temp_list[1:-1]
        hum_list = hum_list[1:-1]

        # calculate average values
        temperature = round(sum(temp_list)/len(temp_list), 1)
        humidity = round(sum(hum_list)/len(hum_list), 1)

        # write to *.CSV file
        f = open('stat.csv', 'a')
        writer = csv.writer(f)
        writer.writerow((tstamp, temperature, humidity))
        f.close()

        # print on screen
        print('AVG\tTemp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity)) + '\n'

        # delay for 30 minutes
        time.sleep(60 * 30)
except KeyboardInterrupt:
    print('\nExit, Goodbye...')
