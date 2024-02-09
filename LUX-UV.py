#LTF390 Light and UV Sensor

import time, board, adafruit_ltr390, requests
from adafruit_ltr390 import LTR390, Resolution

#0x56 -  i2cdetect -y 1

i2c = board.I2C() 
ltr390 = adafruit_ltr390.LTR390(i2c) 


# API URL - probe_temp API interface to hit
LUX_url = "http://localhost:5000/sensors/LUX"
UV_url = "http://localhost:5000/sensors/UV"

#How often to update the API
update_interval = 60  # 1 minutes in seconds


#ltr390.resolution = Resolution.RESOLUTION_18BIT

#ltr390.uvs is UV
#ltr390.uvi is UV Index
#ltr390.light is Ambient Light
#ltr390.lux is LUX


last_update_time = time.time()


while True:
    start_time = time.time()
    while time.time() - start_time <= update_interval:
        time.sleep(15)
        LUX = round(ltr390.lux, 1)
        UV = round (ltr390.uvi, 1)
#        print(LUX, UV)

    current_time = time.time()

    if current_time - last_update_time >= update_interval:

        try:
            response = requests.put(LUX_url, json={'sensor_value': LUX})
            response.raise_for_status()
            time.sleep(0.1)
            response = requests.put(UV_url, json={'sensor_value': UV})
            response.raise_for_status()
#            print("Data sent successfully")
            last_update_time = current_time  # Update last update time
        except requests.exceptions.RequestException as e:
            print("Error:", e)


