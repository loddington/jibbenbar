import machine
import network
import time
import urequests
import esp32

# Define GPIO pins
BUTTON_PIN = 27

# WiFi credentials
WIFI_SSID = "Severn"
WIFI_PASSWORD = "0294498370"

# Server details
SERVER_IP = "Server address of name"
SERVER_PORT = 5000
ENDPOINT_BUTTON = "/sensors/bucket_tips/increment"

# Retry delay
RETRY_DELAY = 5

def connect_wifi():
  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)
  start_time = time.ticks_ms()  # Record start time
  while time.ticks_diff(time.ticks_ms(), start_time) < 30000:  # Timeout after 30 seconds
    if wlan.isconnected():
      print("WiFi Connected:", wlan.ifconfig())
      return
    if not wlan.isconnected():
      print("Connecting to WiFi...")
      try:
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        time.sleep(1)
      except OSError as e:
        if e.args[0] == 118:  # Error code 118 corresponds to "Wifi Internal Error"
          print("Error: Wifi Internal Error. Restarting the script...")
          machine.reset()
        else:
          print("WiFi connection failed:", e)
          return
  print("WiFi connection timed out. Restarting the script...")
  machine.reset()

def make_request_button():
  global request_in_progress  # Flag to avoid multiple requests during button press
  try:
    if not request_in_progress:
      request_in_progress = True
      response = urequests.put("http://{}:{}/{}".format(SERVER_IP, SERVER_PORT, ENDPOINT_BUTTON))
      if response.status_code == 200:
        print("Request Successful")
      else:
        print("Request Failed with status code:", response.status_code)
  except OSError as e:
    print("Exception occurred during request:", e)
    print("Restarting the script...")
    machine.reset()
  finally:
    request_in_progress = False  # Reset flag regardless of success or failure

def disable_unused_pins():
  unused_pins = [4, 5, 12, 13, 14, 15, 25, 26, 32, 33]
  for pin_num in unused_pins:
    pin = machine.Pin(pin_num)
    pin.init(mode=machine.Pin.IN)
	
	
	def main():
  # Disable unused pins
  disable_unused_pins()
  # Configure pins
  button = machine.Pin(BUTTON_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
  esp32.wake_on_ext0(pin=button, level=esp32.WAKEUP_ALL_LOW)
  print('hi - waiting for bucket tip')

  request_in_progress = False  # Flag to indicate ongoing request process

  while True:
    # Enter light sleep
    print("Entering light sleep...")
    time.sleep_ms(1500)
    machine.lightsleep()

    # Code executed after waking from light sleep (button press)
    print("Woke from light sleep! Button pressed.")
    button_pressed_time = 0

    while True:
      if button.value() == 0:  # Button pressed
        button_pressed_time += 1
        print(button_pressed_time)
      else:  # Button released
        if 2 <= button_pressed_time < 2000:
          time.sleep_ms(200)  # Debounce the button
          # Check flag before connection and request
          if not request_in_progress:
            connect_wifi()
            make_request_button()
          else:
            print("Request already in progress. Waiting...")
            time.sleep_ms(1000)  # Short delay if request in progress
          if request_in_progress:  # Disable WiFi only if request successful
            network.WLAN(network.STA_IF).active(False)  # Disable WiFi
            print("WiFi Disabled going back to sleep")
        time.sleep_ms(500)  # Short delay before checking button again
        break  # Exit inner loop after button released
