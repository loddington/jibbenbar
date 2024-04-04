from gpiozero import Button
import time
import requests

# API URL
api_url = "http://localhost:5000/sensors/bucket_tips/increment"

# Set the GPIO pin for the button
button_pin = 16

# Setup the button pin as input with pull-up resistor
button = Button(button_pin, pull_up=True)

# Initialize variables for debounce
button_pressed_time = None
debounce_duration = 0.1  # 100 milliseconds
max_duration = 3.0  # stuck bucket at halfway

# Function to handle button press
def button_pressed_callback():
    global button_pressed_time
    if button.is_pressed:
        if button_pressed_time is None:
            button_pressed_time = time.time()  # Record the time when button is pressed
    else:
        if button_pressed_time is not None:
            end_time = time.time()  # Record the time when button is released
            duration = end_time - button_pressed_time
            if debounce_duration <= duration < max_duration:  # Check if debounce duration has passed but less than max_duration
                print("Button pressed for {:.2f} seconds".format(duration))
                rain_gauge_tip()
            button_pressed_time = None  # Reset button_pressed_time

# Add event listener for button press
button.when_pressed = button_pressed_callback

# Function to handle rain gauge tip events
def rain_gauge_tip():
    try:
        response = requests.put(api_url)

        if response.status_code == 200:
            sensor_data = response.json()
            print("Sensor value incremented successfully:", sensor_data['sensor'], time.ctime())
        else:
            print("Error:", response.text)
            sensor_data = response.json()  # a quick retry on error

    except requests.exceptions.RequestException as e:
        print("Error calling API:", e)


try:
    while True:
        time.sleep(0.1)  # Keep the script running

except KeyboardInterrupt:
    pass  # No cleanup needed with gpiozero
