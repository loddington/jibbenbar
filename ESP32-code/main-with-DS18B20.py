import os
import machine
import network
import urequests
import time
import esp32
import uasyncio as asyncio

machine.freq(80000000)

# WiFi credentials
WIFI_SSID = "XXXXX"
WIFI_PASSWORD = "XXXXX"
SERVER_URL = "http://severn-data.loddington.com:5000/sensors/bucket_tips/increment"
HOSTNAME = "ESP_Jibbenbar_Rain"

BUTTON_PIN = 27  # GPIO 27
RESTART_INTERVAL = 86400  # 24 hours
MIN_PRESS_DURATION = 5  # Minimum press duration in milliseconds

# Configure and start the watchdog timer (timeout: 60 seconds)
wdt = machine.WDT(timeout=60000)

# Restarts the ESP32 
def restart():
    print("Restarting...")
    machine.reset()

# Connect to WiFi
async def connect_wifi(ssid, password, hostname):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.config(dhcp_hostname=hostname)  # Set the hostname for DHCP
    if not wlan.isconnected():
        print(f"Connecting to WiFi as {hostname}...")
        wlan.connect(ssid, password)
        start_time = time.time()
        while not wlan.isconnected():
            if time.time() - start_time > 10:  # 10 seconds timeout
                print("Failed to connect to WiFi")
                return False
    print("Connected to WiFi:", ssid, "with hostname:", hostname)
    return True

# Send PUT request asynchronously with retry mechanism
async def send_put_request():
    max_retries = 5
    retry_delay = 1  # seconds
    put_timeout = 5  # seconds

    for retry_count in range(max_retries):
        try:
            response = urequests.put(SERVER_URL, timeout=put_timeout)
            if response.status_code == 200:
                print("PUT request sent successfully")
                return  # Exit the function if request succeeds
            else:
                print("Error sending PUT request. Status code:", response.status_code)
                response.close()
        except Exception as e:
            print("Exception occurred while sending PUT request:", e)

        # Retry after delay
        print("Retrying PUT request in {} seconds (retry {}/{})".format(retry_delay, retry_count + 1, max_retries))
        await asyncio.sleep(retry_delay)

# Main function
async def main():
    if not await connect_wifi(WIFI_SSID, WIFI_PASSWORD, HOSTNAME):
        print("WiFi connection failed. Restarting...")
        restart()

    button = machine.Pin(BUTTON_PIN, machine.Pin.IN, machine.Pin.PULL_UP)

    # Configure wake-up on button press
    esp32.wake_on_ext0(pin=button, level=esp32.WAKEUP_ALL_LOW)

    start_time = time.time()  # Track script start time

    while True:
        # Check for 24-hour reboot condition
        elapsed_time = time.time() - start_time
        if elapsed_time >= RESTART_INTERVAL:
            print("24-hour interval reached. Rebooting...")
            restart()

        # Check if woken up by button press
        if machine.wake_reason() == machine.PIN_WAKE:
            print("Woken up by button press detected.")
            
            # Immediately check button state
            if button.value() == 0:  # Active low
                print("Button is pressed.")
                press_start_time = time.ticks_ms()
                
                # Wait for button to be released
                while button.value() == 0:
                    pass
                press_duration = time.ticks_ms() - press_start_time

                print("Button press duration:", press_duration, "ms")

                if press_duration > 0:  # Trigger the PUT request for any press
                    print("Button press detected, sending PUT request...")
                    await send_put_request()
                    
                    # Allow time for the PUT request to complete before going back to sleep
                    await asyncio.sleep(1)  # Wait for 1 second to ensure the request is processed
                else:
                    print("No significant button press detected.")
            else:
                print("Button not pressed upon wake.")

        # Feed the watchdog timer
        wdt.feed()
        
        # Going into light sleep if not woken by button
        print("Going into light sleep...")
        time.sleep_ms(1000) 
        machine.lightsleep()

# Main program
try:
    asyncio.run(main())
except Exception as e:
    print("Exception occurred:", e)
    restart()
