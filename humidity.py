import time, board, adafruit_ahtx0, requests

# I2C 
i2c = board.I2C()  # i2cdetect -y 1
sensor = adafruit_ahtx0.AHTx0(i2c)


# API URL - probe_temp API interface to hit
humidity_url = "http://localhost:5000/sensors/humidity"
temp_url = "http://localhost:5000/sensors/backup_temp"

#How often to update the API
update_interval = 60  # 1 minutes in seconds
last_update_time = time.time()


while True:
    start_time = time.time()
    while time.time() - start_time <= update_interval:
        time.sleep(30)
        humidity = round(sensor.relative_humidity, 2)
        temperature = round(sensor.temperature, 2)
        print(humidity, temperature)

    current_time = time.time()

    if current_time - last_update_time >= update_interval:

        try:
            response = requests.put(humidity_url, json={'sensor_value': humidity})
            response.raise_for_status()
            response = requests.put(temp_url, json={'sensor_value': temperature})
            response.raise_for_status()
            print("Data sent successfully")
            last_update_time = current_time  # Update last update time
        except requests.exceptions.RequestException as e:
            print("Error:", e)




