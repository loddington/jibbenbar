#Temperature in direct Sunlight.
# Officially Temperature is recorded in the shade and 1.2m off the ground. But, for a bit of intertest I have mounted a BME280 with an address of IC2 bus address of 0x76 in the same enclosure as the Lux/UV meter. 
# We wont be using the barometric preasure or humidty here, but they might be handy for calibration.

import bme280, smbus2, time, requests
from time import sleep

port = 1
address = 0x76 #Other BME280s may be different check with i2cdetect -y 1
bus = smbus2.SMBus(port)

bme280.load_calibration_params(bus,address)

#while True:
#    bme280_data = bme280.sample(bus,address)
#    humidity  = bme280_data.humidity
#    pressure  = bme280_data.pressure
#    ambient_temperature = bme280_data.temperature
#    height_above_sea_level = 812
#    adjusted_pressure = pressure + ((pressure * 9.80665 * height_above_sea_level)/(287 * (273 + ambient_temperature + (height_above_sea_level/400))))
#    print(humidity, pressure, adjusted_pressure, ambient_temperature)
#    sleep(1)

# API URL - probe_temp API interface to hit
sun_temp_API_url = "http://localhost:5000/sensors/sun_temp"

#How often to update the API
update_interval = 60  # 1 minutes in seconds

last_update_time = time.time()

while True:
    start_time = time.time()
    while time.time() - start_time <= update_interval:
        time.sleep(20)
        bme280_data = bme280.sample(bus,address)
        sun_ambient_temperature = round(bme280_data.temperature, 2)
        print(sun_ambient_temperature)

    current_time = time.time()

    if current_time - last_update_time >= update_interval:

        try:
            response = requests.put(sun_temp_API_url, json={'sensor_value': sun_ambient_temperature})
            response.raise_for_status()
            print("Data sent successfully")
            last_update_time = current_time  # Update last update time
        except requests.exceptions.RequestException as e:
            print("Error:", e)


