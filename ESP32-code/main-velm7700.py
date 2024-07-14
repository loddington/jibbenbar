import os
from machine import Pin, I2C, deepsleep
from veml7700 import VEML7700
import network
import urequests
import time
import json

# VEML7700 library from here https://github.com/palouf34/veml7700

# Set CPU frequency to 80 MHz
machine.freq(80000000)

# Function to connect to WiFi
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print("Connected to WiFi:", ssid)

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
        i2c = I2C(sda=Pin(19), scl=Pin(23))  # Define I2C pins
        sensor = VEML7700(i2c=i2c, it=100, gain=1/8)  # Initialize VEML7700 sensor
        
        # Read light intensity
        lux = sensor.read_lux()
        return lux
    
    except Exception as e:
        print("Exception occurred while reading light intensity:", e)
        return None

# Main loop
def main_loop():
    while True:
        try:
            connect_wifi("XXXXXXX", "XXXXXXXXX")
            light_intensity = read_light_intensity()
            print("Light Intensity:", light_intensity)
            
            if light_intensity is not None:
                data = {"sensor_value": light_intensity}
                if make_put_request("http://severn-data.loddington.com:5000/sensors/lux", data):
                    print("PUT request for light intensity successful")
                else:
                    print("Failed to send light intensity data after retries")
            else:
                print("Failed to read light intensity")

        except Exception as e:
            print("Exception occurred:", e)
        
        print("Waiting for 1 second before entering deep sleep...")
        time.sleep(1)  # 1 second delay
        
        print("Entering deep sleep for 1 minute...")
        deepsleep(1 * 60 * 1000)  # Sleep for 1 minute (60 seconds)

# Run the main loop
if __name__ == "__main__":
    main_loop()
