import machine
import network
import time
import urequests
import esp32
from machine import Pin
from onewire import OneWire
from ds18x20 import DS18X20

# Set sleep duration (milliseconds)
sleep_duration = 60000  # 60 seconds = 60000 milliseconds

# Define GPIO pin for the button
BUTTON_PIN = 27
# Define GPIO pin for the DS18B20 temperature sensor
TEMP_SENSOR_PIN = 19

# Define the WiFi credentials
WIFI_SSID = "Your SSID"
WIFI_PASSWORD = "YOUR SSID PW"

# Define the server IP of the Data Logger API and endpoint
SERVER_IP = "Your-Server-Name-or-IP"
SERVER_PORT = 5000
ENDPOINT_BUCKET = "sensors/bucket_tips/increment"
ENDPOINT_TEMPERATURE = "sensors/sun_temp"

# Define the delay between connection attempts
RETRY_DELAY = 5

# Function to connect to WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
    print("WiFi Connected:", wlan.ifconfig())

# Function to make the HTTP request to the Data Logger
def make_request_bucket():
    try:
        response = urequests.put("http://{}:{}/{}".format(SERVER_IP, SERVER_PORT, ENDPOINT_BUCKET))
        if response.status_code == 200:
            print("Requests Successful")
            response.close()
            return True
        else:
            print("Request(s) Failed:")
            if response.status_code != 200:
                print("  - Request to SERVER_IP failed with status code:", response.status_code)
                # Retry the connection to SERVER_IP after a delay
                print("Retrying connection to SERVER_IP in 5 seconds...")
                time.sleep(5)
                response = urequests.put("http://{}:{}/{}".format(SERVER_IP, SERVER_PORT, ENDPOINT_BUCKET))
                if response.status_code == 200:
                    print("Retried connection to SERVER_IP successful")
                else:
                    print("Retry to SERVER_IP failed, going back to sleep")
                    return False
    except OSError as e:
        if e.errno == 113:
            print("Connection aborted. Data logger may be unreachable.")
        else:
            print("Exception occurred during request:", e)
        return False

def make_request_temperature(temperature):
    try:
        data = {'sensor_value': temperature}
        headers = {'Content-Type': 'application/json'}
        response = urequests.put("http://{}:{}/{}".format(SERVER_IP, SERVER_PORT, ENDPOINT_TEMPERATURE), headers=headers, json=data)
        if response.status_code == 200:
            print("Temperature Request Successful")
            response.close()
            return True
        else:
            print("Temperature Request Failed with status code:", response.status_code)
            return False
    except OSError as e:
        print("Exception occurred during temperature request:", e)
        return False



# Function to read temperature from DS18B20 sensor
def read_temperature():
    dat = Pin(TEMP_SENSOR_PIN)
    ds_sensor = DS18X20(OneWire(dat))
    roms = ds_sensor.scan()
    ds_sensor.convert_temp()
    time.sleep_ms(750)  # Wait for conversion to finish (750ms for DS18B20)
    temperature = ds_sensor.read_temp(roms[0])  # Assuming only one sensor connected
    return temperature

# Main loop
def main():
    # Disable unused peripherals and pins to reduce power consumption
    machine.Pin(4, machine.Pin.IN)  # GPIO4 is disabled
    # machine.lightsleep()  # Start in light sleep mode
    print('hi')

    # Configure button pin with pull-up
    button = machine.Pin(BUTTON_PIN, machine.Pin.IN, machine.Pin.PULL_UP)

    while True:
        temperature = read_temperature()  # Read temperature
        print("DS18B20 Temperature reading is:", temperature)  # Print temperature reading
        make_request_temperature(temperature)  # Send temperature reading to server
        
        time.sleep(0.5) #This is just for debugging. 
        machine.lightsleep(sleep_duration)  # Sleep 

        # Check for button press after waking up from light sleep
        if button.value() == 0:  # Button is pressed
            print("Button pressed!")
            # Your button handling code here (e.g., connect to WiFi, send data)
            connect_wifi()
            if make_request_bucket():
                time.sleep_ms(200)
                network.WLAN(network.STA_IF).active(False)  # Disable WiFi
                print("WiFi Disabled going back to sleep")
            else:
                print("Retrying in {} seconds...".format(RETRY_DELAY))
                time.sleep(RETRY_DELAY)

if __name__ == "__main__":
    main()
