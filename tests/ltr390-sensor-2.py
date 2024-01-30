# SPDX-FileCopyrightText: 2021 by Bryan Siepert, written for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
import time
import board
import adafruit_ltr390
from adafruit_ltr390 import LTR390, MeasurementDelay, Resolution


i2c = board.I2C()  
ltr = adafruit_ltr390.LTR390(i2c) 

#ltr.resolution = Resolution.RESOLUTION_18BIT


while True:
    print("UV:", ltr.uvs, "\t\tAmbient Light:", ltr.light)
    print("UVI:", ltr.uvi, "\t\tLux:", ltr.lux)
    time.sleep(1.0)# SPDX-FileCopyrightText: 2021 by Bryan Siepert, written for Adafruit Industries
