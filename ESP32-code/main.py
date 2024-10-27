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

BUTTON_PIN = 27
RESTART_INTERVAL = 86400  # 24 hours in seconds
MIN_PRESS_DURATION = 5
MAX_PRESS_DURATION = 5000

# Watchdog timer (timeout: 60 seconds)
wdt = machine.WDT(timeout=60000)

# Restart ESP32
def restart():
    print("Restarting...")
    machine.reset()

# Connect to WiFi with auto-reconnect and hostname
async def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # Set the hostname for DHCP
    esp32.wifi_set_hostname("ESP32_Sensor_Node")  # Replace with your desired hostname

    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            await asyncio.sleep_ms(100)
    print("Connected to WiFi:", wlan.ifconfig())
    wdt.feed()

# Send PUT request with retries
async def send_put_request():
    max_retries = 2
    retry_delay = 1
    put_timeout = 5

    for retry_count in range(max_retries):
        try:
            response = urequests.put(SERVER_URL, timeout=put_timeout)
            if response.status_code == 200:
                print("PUT request sent successfully")
                response.close()
                return
            else:
                print("Error:", response.status_code)
                response.close()
        except Exception as e:
            print("Exception:", e)

        print("Retrying in {}s (try {}/{})".format(retry_delay, retry_count + 1, max_retries))
        await asyncio.sleep(retry_delay)

    print("Max retries reached.")

# Main function
async def main():
    await connect_wifi()
    button = machine.Pin(BUTTON_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
    esp32.wake_on_ext0(pin=button, level=esp32.WAKEUP_ALL_LOW)

    start_time = time.time()  # Track script start time

    while True:
        # Check for 24-hour reboot condition
        elapsed_time = time.time() - start_time
        if elapsed_time >= RESTART_INTERVAL:
            print("24-hour interval reached. Rebooting...")
            restart()

        print("Going into light sleep...")
        await asyncio.sleep(1)
        machine.lightsleep()
        print("Woke up from light sleep")

        if machine.wake_reason() == machine.PIN_WAKE:
            start_time = time.ticks_ms()
            while button.value() == 0:
                pass
            press_duration = time.ticks_ms() - start_time

            print("Button press duration:", press_duration, "ms")

            if press_duration >= MIN_PRESS_DURATION:
                print("Button press detected")
                await send_put_request()

        wdt.feed()
        await asyncio.sleep(0.15)

# Main program
try:
    asyncio.run(main())
except Exception as e:
    print("Exception occurred:", e)
    restart()
