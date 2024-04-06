import machine
import network
import time
import urequests
import esp32
from onewire import OneWire
from ds18x20 import DS18X20

machine.freq(80000000)

# Define GPIO pin for the button
BUTTON_PIN = 27

# Define the WiFi credentials
WIFI_SSID = "JibbenbarSSID"
WIFI_PASSWORD = "Your-WiFi-PW"

# Define the server IP of the Data Logger API and endpoint
SERVER_IP = "severn-data.loddington.com"
SERVER_PORT = 5000
TEMPERATURE_ENDPOINT = "/sensors/temperature/increment"
BUTTON_ENDPOINT = "/sensors/button/press"

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

# Function to make the HTTP request to the Data Logger for button press
def send_button_press():
    try:
        response = urequests.put("http://{}:{}/{}".format(SERVER_IP, SERVER_PORT, BUTTON_ENDPOINT))
        if response.status_code == 200:
            print("Button press sent successfully")
        else:
            print("Failed to send button press")
        response.close()
    except OSError as e:
        print("Exception occurred during button press request:", e)

# Function to make the HTTP request to the Data Logger for temperature
def send_temperature(temperature):
    try:
        response = urequests.put("http://{}:{}/{}".format(SERVER_IP, SERVER_PORT, TEMPERATURE_ENDPOINT), json={"temperature": temperature})
        if response.status_code == 200:
            print("Temperature sent successfully")
        else:
            print("Failed to send temperature")
        response.close()
    except OSError as e:
        print("Exception occurred during temperature request:", e)

# Main loop
def main():
    # Disable unused peripherals and pins to reduce power consumption
    machine.Pin(2, machine.Pin.IN)  # GPIO2 is disabled
    #machine.Pin(4, machine.Pin.IN)  # GPIO4 is disabled
    machine.Pin(5, machine.Pin.IN)  # GPIO5 is disabled
    machine.Pin(12, machine.Pin.IN) # GPIO12 is disabled
    machine.Pin(13, machine.Pin.IN) # GPIO13 is disabled
    machine.Pin(14, machine.Pin.IN) # GPIO14 is disabled
    machine.Pin(15, machine.Pin.IN) # GPIO15 is disabled
    machine.Pin(25, machine.Pin.IN) # GPIO25 is disabled
    machine.Pin(26, machine.Pin.IN) # GPIO26 is disabled
    #machine.Pin(27, machine.Pin.IN) # GPIO27 is disabled
    machine.Pin(32, machine.Pin.IN) # GPIO32 is disabled
    machine.Pin(33, machine.Pin.IN) # GPIO33 is disabled
    print('hi')
  
    # Initialize DS18X20 sensor
    ow = OneWire(machine.Pin(4))  # Pin where DS18D20 sensor is connected
    ds = DS18X20(ow)

    while True:
        # Configure button pin with pull-up and wakeup capability
        button = machine.Pin(BUTTON_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
        esp32.wake_on_ext0(pin=button, level=esp32.WAKEUP_ALL_LOW)

        # Enter light sleep
        print("Entering light sleep...")
        time.sleep_ms(1500)
        machine.lightsleep()

        # Code executed after waking from light sleep (button press)
        print("Woke from light sleep! Button pressed.")
        button = machine.Pin(BUTTON_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
        button_pressed_time = 0

        while True:
            if button.value() == 0:  # Button is pressed
                button_pressed_time += 1
            else:  # Button released
                if 100 <= button_pressed_time < 1000:
                    time.sleep_ms(500)  # Debounce the button
                    connect_wifi()
                    send_button_press()
                    time.sleep_ms(200)
                    network.WLAN(network.STA_IF).active(False)  # Disable WiFi
                    print("WiFi Disabled going back to sleep")
                    time.sleep_ms(500)
                    machine.lightsleep()
                button_pressed_time = 0

            # Check temperature every 15 minutes
            if time.time() % 900 == 0:  # 900 seconds = 15 minutes
                ds.convert_temp()
                time.sleep_ms(750)
                temperature = ds.read_temp()
                if temperature is not None:
                    print("Temperature:", temperature)
                    connect_wifi()
                    send_temperature(temperature)
                    time.sleep_ms(200)
                    network.WLAN(network.STA_IF).active(False)  # Disable WiFi
                    print("WiFi Disabled going back to sleep")
                    time.sleep_ms(500)
                    machine.lightsleep()

if __name__ == "__main__":
    main()
