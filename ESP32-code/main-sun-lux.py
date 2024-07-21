import os
from machine import Pin, SoftI2C, deepsleep
from veml7700 import VEML7700  # Ensure this library is available
import network
import urequests
import time
import json
import machine
import onewire
import ds18x20

#LioLin ESP32 S2 Mini 

# Set CPU frequency to 80 MHz if needed
# machine.freq(80000000)

# Function to connect to WiFi
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(ssid, password)
        start_time = time.time()
        while not wlan.isconnected():
            if time.time() - start_time > 10:  # 10 seconds timeout
                print("Failed to connect to WiFi")
                return False
            pass
    print("Connected to WiFi:", ssid)
    return True

# Function to make PUT request with retry and timeout
def make_put_request(url, data, retries=3, timeout=5):
    try_count = 0
    while try_count < retries:
        try:
            headers = {'Content-Type': 'application/json'}
            response = urequests.put(url, data=json.dumps(data), headers=headers, timeout=timeout)
            response.close()
            if response.status_code == 200:
                return True
            else:
                print("PUT request failed with status code:", response.status_code)
                try_count += 1
        except Exception as e:
            print("Exception occurred during PUT request:", e)
            try_count += 1
    return False

# Function to read light intensity from VEML7700 sensor
def read_light_intensity():
    try:
        i2c = SoftI2C(sda=Pin(9), scl=Pin(8))  # Define I2C pins
        sensor = VEML7700(i2c=i2c, it=100, gain=1/8)  # Initialize VEML7700 sensor
        lux = sensor.read_lux()
        return lux
    except Exception as e:
        print("Exception occurred while reading light intensity:", e)
        return None

# Function to read temperature from DS18B20 sensor
def read_temperature():
    try:
        ow = onewire.OneWire(machine.Pin(5))  # Pin 5 is used for DS18B20 data line
        ds = ds18x20.DS18X20(ow)
        roms = ds.scan()
        ds.convert_temp()
        time.sleep_ms(750)
        temperature = ds.read_temp(roms[0])
        return temperature
    except Exception as e:
        print("Exception occurred while reading temperature:", e)
        return None

# Main loop
def main_loop():
    while True:
        try:
            if connect_wifi("XXXXXXXX", "XXXXXXXXXXX"):
                light_intensity = read_light_intensity()
                temperature_reading = read_temperature()
                print("Light Intensity:", light_intensity)
                print("Temperature in the Sun:", temperature_reading)

                if light_intensity is not None:
                    data = {"sensor_value": light_intensity}
                    if make_put_request("http://192.168.167.30:5000/sensors/lux", data):
                        print("PUT request for light intensity successful")
                    else:
                        print("Failed to send light intensity data after retries")
                else:
                    print("Failed to read light intensity")
                    
                if temperature_reading is not None:
                    data = {"sensor_value": temperature_reading}
                    if make_put_request("http://192.168.167.30:5000/sensors/sun_temp", data):
                        print("PUT request for temperature in the sun is successful")
                    else:
                        print("Failed to send temperature in the sun data after retries")
                else:
                    print("Failed to read temperature in the sun")    

        except Exception as e:
            print("Exception occurred:", e)

        print("Waiting for 3 seconds before entering deep sleep...")
        time.sleep(3)  # 3 seconds delay

        print("Entering deep sleep for 7 minutes...")
        deepsleep(7 * 60 * 1000)  # Sleep for 7 minutes

# Run the main loop
if __name__ == "__main__":
    main_loop()
