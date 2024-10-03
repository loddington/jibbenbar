import RPi.GPIO as GPIO
import time
import requests

# Set up the GPIO mode
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin where the button is connected
button_pin = 13  # Change to your button pin number

# API URL
api_url = "http://localhost:5000/sensors/bucket_tips/increment"

# Set up the button pin as an input with a pull-up resistor
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Debounce delay (50 ms)
debounce_duration = 0.05  # 50 milliseconds

def button_pressed_duration():
    press_time = None
    release_time = None

    try:
        while True:
            # Wait for the button press (GPIO input goes low)
            if GPIO.input(button_pin) == GPIO.LOW:
                time.sleep(debounce_duration)  # Debounce delay to filter out mechanical bounce
                
                # Check if the button is still pressed after debounce delay
                if GPIO.input(button_pin) == GPIO.LOW:
                    press_time = time.time()  # Record the press time
                    print("Button pressed!")

                    # Wait for the button release (GPIO input goes high)
                    while GPIO.input(button_pin) == GPIO.LOW:
                        time.sleep(0.01)  # Small delay to prevent busy-waiting

                    release_time = time.time()  # Record the release time
                    duration = release_time - press_time  # Calculate press duration
                    print(f"Button was pressed for {duration:.2f} seconds")
                    rain_gauge_tip()

            time.sleep(0.1)  # Short delay to prevent CPU overuse

    except KeyboardInterrupt:
        print("Exiting program")

    finally:
        GPIO.cleanup()  # Clean up the GPIO on exit

# Function to handle rain gauge tip events
def rain_gauge_tip():
    try:
        response = requests.put(api_url)
        if response.status_code == 200:
            sensor_data = response.json()
            print(f"Sensor value incremented successfully: {sensor_data['sensor']}, {time.ctime()}")
        else:
            print("Error:", response.text)
    except requests.exceptions.RequestException as e:
        print("Error calling API:", e)

# Add a small delay before setting up event detection (to ensure pin stability)
time.sleep(0.2)

if __name__ == "__main__":
    button_pressed_duration()
