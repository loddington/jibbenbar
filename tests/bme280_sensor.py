import bme280
import smbus2
from time import sleep

port = 1
address = 0x77 # soem use 0x77 others use 0x76 - check with: ic2detect -y 1
bus = smbus2.SMBus(port)

height_above_sea_level = 812 #meters

bme280.load_calibration_params(bus,address)

while True:
    bme280_data = bme280.sample(bus,address)
    humidity  = bme280_data.humidity
    pressure  = bme280_data.pressure
    ambient_temperature = bme280_data.temperature
    adjusted_pressure = pressure + ((pressure * 9.80665 * height_above_sea_level)/(287 * (273 + ambient_temperature + (height_above_sea_level/400))))
    print(humidity, pressure, adjusted_pressure, ambient_temperature)
    sleep(1)




