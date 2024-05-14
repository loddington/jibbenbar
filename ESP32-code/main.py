# Import the necessary modules
import machine
import network
import urequests
import time
import esp32
import uasyncio as asyncio

machine.freq(80000000)

# WiFi credentials
WIFI_SSID = "XXXXXXX"
WIFI_PASSWORD = "XXXXXXX"
SERVER_URL = "http://lod-data.loddington.com:5000/sensors/bucket_tips_2/increment"

BUTTON_PIN = 27  # GPIO 14
RESTART_INTERVAL = 86400
MIN_PRESS_DURATION = 5  # Minimum press duration in milliseconds
MAX_PRESS_DURATION = 5000

# Configure and start the watchdog timer (timeout: 60 seconds)
wdt = machine.WDT(timeout=60000)

# Restarts the ESP32 
def restart():
    print("Restarting...")
    machine.reset()

# Connect to WiFi asynchronously
async def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            await asyncio.sleep_ms(100)
    print("Connected to WiFi:", wlan.ifconfig())
    # Feed the watchdog timer after successful WiFi connection
    wdt.feed()

# Send PUT request asynchronously with retry mechanism and increased timeout
async def send_put_request():
    max_retries = 2
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

    print("Max retries reached, unable to send PUT request")

# Main function
async def main():
    await connect_wifi()

    button = machine.Pin(BUTTON_PIN, machine.Pin.IN, machine.Pin.PULL_UP)

    # Configure wake-up on button press
    esp32.wake_on_ext0(pin=button, level=esp32.WAKEUP_ALL_LOW)

    while True:
        print("Going into light sleep...")
        await asyncio.sleep(1)
        machine.lightsleep()
        print("Woke up from light sleep")

        # Check if woken up by button press
        if machine.wake_reason() == machine.PIN_WAKE:
            # Measure button press duration
            start_time = time.ticks_ms()
            while button.value() == 0:
                pass
            end_time = time.ticks_ms()
            press_duration = end_time - start_time

            print("Button press duration:", press_duration, "ms")

            if press_duration >= MIN_PRESS_DURATION:
                print("Woken up by button press")
                await send_put_request()

        # Feed the watchdog timer after waking up
        wdt.feed()

        await asyncio.sleep(0.15)

# Main program
try:
    asyncio.run(main())
except Exception as e:
    print("Exception occurred:", e)
    restart()
