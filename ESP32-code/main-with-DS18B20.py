import machine
import time
import onewire
import ds18x20
import network
import urequests as requests  
#script for UV and Tempurature - Wont work with tipping bucket as that uses light sleep and I cant get it to place nice with the button press

# WiFi credentials
WIFI_SSID = "YourSSID"
WIFI_PASSWORD = "WiFiPW"

# API endpoints - Change to your endpoints
UV_API_ENDPOINT = "http://jibbenbar-data.loddington.com:5000/sensors/UV"
TEMP_API_ENDPOINT = "http://jibbendar-data.loddington.com:5000/sensors/sun_temp"

# Define DS18B20 data pin
DS18B20_PIN = 19  # Updated pin for DS18B20 sensor

# Define analog pin for GUVA-S12SD sensor
GUVA_S12SD_PIN = 14  # Updated pin for GUVA-S12SD sensor

# Calibration parameters for UV index mapping
VOLTAGE_MIN = 0.0  # Minimum output voltage
VOLTAGE_MAX = 3.3  # Maximum output voltage
UV_INDEX_MIN = 0    # Minimum UV index value
UV_INDEX_MAX = 12   # Maximum UV index value

# Disable unused pins
UNUSED_PINS = [3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]

def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            pass
    print("Connected to WiFi:", wlan.ifconfig())

def read_temperature():
    # Setup DS18B20 sensor
    ow = onewire.OneWire(machine.Pin(DS18B20_PIN))
    ds = ds18x20.DS18X20(ow)
    roms = ds.scan()

    # Read temperature from the first DS18B20 sensor found
    ds.convert_temp()
    time.sleep_ms(750)
    temperature = ds.read_temp(roms[0])
    return temperature

def read_uv_intensity():
    # Read analog voltage from GUVA-S12SD sensor
    adc = machine.ADC(machine.Pin(GUVA_S12SD_PIN))
    uv_voltage = adc.read() * (3.3 / 4095)  # Convert ADC value to voltage
    return uv_voltage

def map_voltage_to_uv_index(voltage):
    # Map the voltage reading to the UV index range
    uv_index = UV_INDEX_MIN + (voltage - VOLTAGE_MIN) * (UV_INDEX_MAX - UV_INDEX_MIN) / (VOLTAGE_MAX - VOLTAGE_MIN)
    return uv_index

def send_temperature(temperature):
    try:
        print("Sending temperature data to API...")
        payload = {'sensor_value': temperature}
        response = requests.put(TEMP_API_ENDPOINT, json=payload)
        print("Response from temperature server:", response.text)
        response.close()
        return response.text  # Return response for further processing
    except Exception as e:
        print("Error sending temperature data to API:", e)

def send_uv_index(uv_index):
    try:
        print("Sending UV index data to API...")
        payload = {'sensor_value': uv_index}
        response = requests.put(UV_API_ENDPOINT, json=payload)
        print("Response from UV server:", response.text)
        response.close()
        return response.text  # Return response for further processing
    except Exception as e:
        print("Error sending UV index data to API:", e)

def deep_sleep(seconds):
    print("Entering deep sleep mode for {} seconds...".format(seconds))
    for pin in UNUSED_PINS:
        machine.Pin(pin, machine.Pin.IN)
    time.sleep_ms(2000)  # 2-second delay before sleeping
    machine.deepsleep(seconds * 1000)

def main():
    try:
        connect_to_wifi()
        temperature = read_temperature()
        uv_voltage = read_uv_intensity()
        uv_index = map_voltage_to_uv_index(uv_voltage)
        temp_response = send_temperature(temperature)
        uv_response = send_uv_index(uv_index)
        # Process responses as needed
        print("Temperature Response:", temp_response)
        print("UV Index Response:", uv_response)
    except Exception as e:
        print("Error:", e)
    finally:
        # Enter deep sleep for 12 seconds for testing
        deep_sleep(12)

# Run the main function
if __name__ == "__main__":
    main()
