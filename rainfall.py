import RPi.GPIO as GPIO
import requests
import time

#A scrip to run in the background waiting for the rain bucket to tip and then update the API

# Set GPIO pin mode to BCM
GPIO.setmode(GPIO.BCM)

# Define GPIO pin 6 as an input
pin = 6
# GPIO.setup(pin, GPIO.IN)
GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# URL to call when bucket is tipped
#curl -d '{"id":"bucket_tips"}' -H "Content-Type: application/json" -X PUT http://localhost:5000/sensors/bucket_tips/increment

#URL to call to get the values from the flask api data collector
#curl  -H "Content-Type: application/json"  -X GET http://localhost:5000/sensors/bucket_tips

#URL To call to reset the counter to 0 
#curl -d '{"id":"bucket_tips","sensor_value":"0"}' -H "Content-Type: application/json" -X PUT http://localhost:5000/sensors/bucket_tips

# URL
api_url = "http://localhost:5000/sensors/bucket_tips/increment"

# Sensor to hit
sensor_id = "bucket_tips"


# Function to handle rain gauge tip events
def rain_gauge_tip(channel):
	try:
		response = requests.put(api_url)

		if response.status_code == 200:
			sensor_data = response.json()
			print("Sensor value incremented successfully:", sensor_data['sensor'])
		else:
			print("Error:", response.text)

	except requests.exceptions.RequestException as e:
		print("Error  calling API:", e)



# Attach an interrupt to GPIO pin 6 and call the rain_gauge_tip function on a rising edge
GPIO.add_event_detect(pin, GPIO.RISING, callback=rain_gauge_tip, bouncetime=300)

# Keep the script running indefinitely
while True:
    time.sleep(0.5)
