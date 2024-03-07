import time, board, adafruit_bme680, requests, configparser

# I2C
i2c = board.I2C()  # i2cdetect -y 1
sensor =  adafruit_bme680.Adafruit_BME680_I2C(i2c, debug=False)


config = configparser.ConfigParser()
config.sections()
config.read('config.ini')

temperature_offset = float(config['temperature_offset']['temperature_offset'])
# -0.3

height_above_sea_level = float(config['altitude']['height_above_sea_level'])



# API URL - probe_temp API interface to hit
humidity_url = "http://localhost:5000/sensors/humidity"
temp_url = "http://localhost:5000/sensors/backup_temp"
barometric_pressure_url = "http://localhost:5000/sensors/barometric_pressure"


# You can do this by hand by using:
# curl  -H "Content-Type: application/json"  -X GET http://localhost:5000/sensors


#How often to update the API
update_interval = 60  # 1 minutes in seconds
last_update_time = time.time()


while True:
    start_time = time.time()
    while time.time() - start_time <= update_interval:
        time.sleep(15)
        humidity = round(sensor.relative_humidity, 2)
        raw_temperature = (round(sensor.temperature, 2) + temperature_offset)
        temperature = round(raw_temperature, 2)
        pressure = round(sensor.pressure, 2)
        adjusted_pressure = pressure + ((pressure * 9.80665 * height_above_sea_level)/(287 * (273 + temperature + (height_above_sea_level/400))))
        barometric_pressure = round(adjusted_pressure, 2)
        print(humidity, temperature, pressure, barometric_pressure)
        if pressure < 700:
             print("Invalid pressure reading, retrying...")
             time.sleep(3)
             continue
    current_time = time.time()

    if current_time - last_update_time >= update_interval:

        try:
            response = requests.put(humidity_url, json={'sensor_value': humidity})
            response.raise_for_status()
            response = requests.put(temp_url, json={'sensor_value': temperature})
            response.raise_for_status()
            response = requests.put(barometric_pressure_url, json={'sensor_value': barometric_pressure})
            response.raise_for_status()
            print("Data sent successfully")
            print(humidity, temperature, barometric_pressure)
            last_update_time = current_time  # Update last update time
        except requests.exceptions.RequestException as e:
            print("Error:", e)

