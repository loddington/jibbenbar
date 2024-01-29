#The ATH20 sensor I am using also contains a BMP280 on 0x77. The ATH20 provides Humidity and Temperature. The BMP280 provides air preasure and Temperature.
#The ATH20 sensor board was cheaper than a BME280 and appears to be more reliable.  
#Note the difference between a BMP280 and a BME280 is the BME280 records Humidty too. I seem to keep ordering BME280s and BMP280s turn up. 
#I'm not going to record the temperature to the API, but it is used in the adjusted preasure measurement and handy to use it to correlate the temperatures from the DS18B20 Probe and the ATH20.

import bme280, smbus2, requests, time
from time import sleep

port = 1
address = 0x77 # some BMP280/BME280 use 0x77 others use 0x76 - check with: ic2detect -y 1
bus = smbus2.SMBus(port)

height_above_sea_level = 812 #meters

bme280.load_calibration_params(bus,address)

# API URL - probe_temp API interface to hit
barometer_API_url = "http://localhost:5000/sensors/barometer"

#How often to update the API
update_interval = 60  # 1 minutes in seconds


#while True:
#    bme280_data = bme280.sample(bus,address)
#    humidity  = bme280_data.humidity
#    ambient_temperature = bme280_data.temperature
#    pressure  = bme280_data.pressure
#    adjusted_pressure = pressure + ((pressure * 9.80665 * height_above_sea_level)/(287 * (273 + ambient_temperature + (height_above_sea_level/400))))
#    print(humidity, pressure, adjusted_pressure, ambient_temperature)
#    sleep(1)


last_update_time = time.time()


while True:
    start_time = time.time()
    while time.time() - start_time <= update_interval:
        time.sleep(30)
        bme280_data = bme280.sample(bus,address)
        pressure  = bme280_data.pressure
        ambient_temperature = bme280_data.temperature
        adjusted_pressure = pressure + ((pressure * 9.80665 * height_above_sea_level)/(287 * (273 + ambient_temperature + (height_above_sea_level/400))))
        barometric_preassure = round(adjusted_pressure, 2)
        print(barometric_preassure)

    current_time = time.time()

    if current_time - last_update_time >= update_interval:

        try:
            response = requests.put(barometer_API_url, json={'sensor_value': barometric_preassure})
            response.raise_for_status()
            print("Data sent successfully")
            last_update_time = current_time  # Update last update time
        except requests.exceptions.RequestException as e:
            print("Error:", e)


