import machine
import network
import time
import urequests
import esp32

machine.freq(80000000)


# Define GPIO pin for the button
BUTTON_PIN = 27

# Define the WiFi credentials
WIFI_SSID = "JibbenbarWiFI"
WIFI_PASSWORD = "YourWiFiPWDHere"

# Define the server IP of the Data Logger API and endpoint
SERVER_IP = "192.168.1.30" 
SERVER_PORT = 5000
ENDPOINT = "/sensors/bucket_tips/increment"

# Define the delay between connection attempts
RETRY_DELAY = 10

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
def make_request():
    try:
        response = urequests.put("http://{}:{}/{}".format(SERVER_IP, SERVER_PORT, ENDPOINT))
        if response.status_code == 200:
            print("Request Successful")
            response.close()
            return True
        else:
            print("Request Failed:", response.status_code)
            response.close()
            return False
    except Exception as e:
        print("Exception occurred during request:", e)
        return False

# Main loop
def main():
    # Disable unused peripherals and pins to reduce power consumption
    machine.Pin(2, machine.Pin.IN)  # GPIO2 is disabled
    machine.Pin(4, machine.Pin.IN)  # GPIO4 is disabled
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
    
    print('Jibbenbar Weather ESP32 Rain Tipping Bucket')
  
    while True:
	    # Configure button pin with pull-up and wakeup capability
        button = machine.Pin(BUTTON_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
        esp32.wake_on_ext0(pin=button, level=esp32.WAKEUP_ALL_LOW)

    # Enter light sleep
        print("Entering light sleep...")
        time.sleep_ms(1000)
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
                    if make_request():
                        time.sleep_ms(5000)
                        network.WLAN(network.STA_IF).active(False)  # Disable WiFi
                        print("WiFi Disabled going back to sleep")
                        time.sleep_ms(500)
                        machine.lightsleep()
                    else:
                        print("Retrying in {} seconds...".format(RETRY_DELAY))
                        time.sleep(RETRY_DELAY)
                button_pressed_time = 0
                


if __name__ == "__main__":
    main()



