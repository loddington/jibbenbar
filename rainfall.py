import RPi.GPIO as GPIO
import time
import requests

# After getting lots of weird false posiitves I moved to checking how long the button / reed switch was activated for. Problem solved!

# I am now using a home made tipping bucket sensor rather than the Maplin. https://www.printables.com/model/130513-rain-gauge - It is larger and more robust unit and has a 0.2mm tip rthan than the 0.2794mm of the Maplin.


# API URL
api_url = "http://localhost:5000/sensors/bucket_tips/increment"

# You can see what is in the Data logger by using this command:
# curl  -H "Content-Type: application/json"  -X GET http://localhost:5000/sensors


# Set the GPIO mode
GPIO.setmode(GPIO.BCM)

# Set the GPIO pin for the button
button_pin = 19

# Setup the button pin as input with pull-up resistor
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize variables for debounce
button_pressed_time = None
debounce_duration = 0.1  # 100 milliseconds

# Function to handle button press
def button_pressed_callback(channel):
    global button_pressed_time
    if GPIO.input(channel) == GPIO.LOW:
        if button_pressed_time is None:
            button_pressed_time = time.time()  # Record the time when button is pressed
    else:
        if button_pressed_time is not None:
            end_time = time.time()  # Record the time when button is released
            duration = end_time - button_pressed_time
            if duration >= debounce_duration:  # Check if debounce duration has passed
                print("Button pressed for {:.2f} seconds".format(duration))
                rain_gauge_tip(channel)
            button_pressed_time = None  # Reset button_pressed_time

# Add event listener for button press
GPIO.add_event_detect(button_pin, GPIO.BOTH, callback=button_pressed_callback)


# Function to handle rain gauge tip events
def rain_gauge_tip(channel):
    try:
        response = requests.put(api_url)

        if response.status_code == 200:
            sensor_data = response.json()
            print("Sensor value incremented successfully:", sensor_data['sensor'], time.ctime())
        else:
            print("Error:", response.text)
            sensor_data = response.json() # a quick retry on error

    except requests.exceptions.RequestException as e:
        print("Error calling API:", e)



try:
    while True:
        time.sleep(0.1)  # Keep the script running

except KeyboardInterrupt:
    GPIO.cleanup()  # Clean up GPIO on Ctrl+C exit














