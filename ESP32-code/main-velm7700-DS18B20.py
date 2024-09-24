import os
from machine import Pin, SoftI2C, deepsleep, RTC, reset, WDT
from veml7700 import VEML7700  # Ensure this library is available
import network
import urequests
import time
import json
import machine
import onewire
import ds18x20

# Initialize RTC for saving data during deep sleep and tracking uptime
rtc = machine.RTC()

# WiFi credentials
SSID = "XXXXXXXXXXX"
PASSWORD = "XXXXXXXXXXXX"

# Constants
REBOOT_TIME_MINUTES = 12 * 60  # 1440 minutes for a 12-hour reboot

# Initialize Watchdog Timer with 8-second timeout
wdt = WDT(timeout=15000)

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
    print("Connected to WiFi:", ssid)
    return True

# Function to ensure WiFi is connected
def ensure_wifi_connected(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print("WiFi disconnected, reconnecting...")
        return connect_wifi(ssid, password)
    return True

# Function to make PUT request with retry and exponential backoff
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
            print("Exception during PUT request, attempt:", try_count, "Error:", e)
            try_count += 1
            time.sleep(2 ** try_count)  # Exponential backoff
    return False

# Function to store last readings in RTC memory
def store_last_readings(light_intensity, temperature):
    data = {}
    if light_intensity is not None:
        data['light'] = light_intensity
    if temperature is not None:
        data['temperature'] = temperature
    rtc.memory(json.dumps(data))

# Function to retrieve last readings from RTC memory
def get_last_readings():
    data = rtc.memory()
    if data:
        return json.loads(data)
    return None

# Function to read light intensity from VEML7700 sensor with retries
def read_light_intensity(retries=3):
    for attempt in range(retries):
        try:
            i2c = SoftI2C(sda=Pin(8), scl=Pin(9))  # Define I2C pins
            sensor = VEML7700(i2c=i2c, it=100, gain=1/8)
            lux = sensor.read_lux()
            return lux
        except Exception as e:
            print(f"Retry {attempt + 1} reading light sensor, Error:", e)
    return None  # Return None after retries

# Function to read temperature from DS18B20 sensor with retries
def read_temperature(retries=3):
    for attempt in range(retries):
        try:
            ow = onewire.OneWire(machine.Pin(3))  # Pin 3 is used for DS18B20 data line
            ds = ds18x20.DS18X20(ow)
            roms = ds.scan()
            ds.convert_temp()
            time.sleep_ms(1000)
            temperature = ds.read_temp(roms[0])
            return temperature
        except Exception as e:
            print(f"Retry {attempt + 1} reading temperature sensor, Error:", e)
    return None  # Return None after retries

# Fallback temperature retrieval using last known value from RTC memory
def read_temperature_with_fallback():
    temperature = read_temperature()
    if temperature is None:
        last_data = get_last_readings()
        if last_data and 'temperature' in last_data:
            print("Using fallback temperature value from RTC")
            return last_data['temperature']
    return temperature

# Function to check if it's time to reboot after 12 hours
def check_for_reboot():
    uptime_seconds = time.ticks_ms() / 1000  # Time in seconds since boot
    uptime_minutes = uptime_seconds / 60
    if uptime_minutes >= REBOOT_TIME_MINUTES:
        print("Rebooting after 12 hours uptime...")
        machine.reset()

# Main loop
def main_loop():
    while True:
        try:
            # Feed the watchdog timer
            wdt.feed()

            check_for_reboot()  # Check if 12 hours have passed and reboot if necessary

            if ensure_wifi_connected(SSID, PASSWORD):
                light_intensity = read_light_intensity()
                temperature_reading = read_temperature_with_fallback()

                if light_intensity is not None:
                    print("Light Intensity:", light_intensity)
                    store_last_readings(light_intensity, None)  # Store partial data
                    data = {"sensor_value": light_intensity}
                    if make_put_request("http://XXXXXXXXXXXXXXXX:5000/sensors/lux", data):
                        print("PUT request for light intensity successful")
                    else:
                        print("Failed to send light intensity data after retries")
                else:
                    print("Failed to read light intensity")

                if temperature_reading is not None:
                    print("Temperature in the Sun:", temperature_reading)
                    store_last_readings(None, temperature_reading)  # Store partial data
                    data = {"sensor_value": temperature_reading}
                    if make_put_request("http://XXXXXXXXXXXXX:5000/sensors/sun_temp", data):
                        print("PUT request for temperature in the sun successful")
                    else:
                        print("Failed to send temperature in the sun data after retries")
                else:
                    print("Failed to read temperature in the sun")

        except Exception as e:
            print("Main loop exception:", e)

        print("Waiting for 4 seconds before entering deep sleep...")
        time.sleep(4)  # Slightly longer delay to ensure everything is settled

        print("Entering deep sleep for 7 minutes...")
        deepsleep(7 * 60 * 1000)  # Sleep for 7 minutes

# Run the main loop
if __name__ == "__main__":
    main_loop()
