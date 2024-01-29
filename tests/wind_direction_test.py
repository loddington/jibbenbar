#Wind Direction test.
#Map the voltages to the compass points.

from gpiozero import MCP3008
import time, math, statistics, requests

check_interval = 1 

adc = MCP3008(channel=0) #Check which channel you are using. Most people will use 0
direction_count = 0 

#Recorded voltages
volts = [0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 1.2, 1.4, 1.8, 2.0, 2.2, 2.5, 2.7, 2.8, 2.9]

#Map voltages to compass points

dict = {}
dict[0.1] = '270' #West
dict[0.2] = '315' #NW
dict[0.3] = '292' #WNW
dict[0.4] = '0'   #North 
dict[0.6] = '337' #NNW 
dict[0.7] = '225' #SW 
dict[0.8] = '247' #WSW 
dict[1.2] = '45'  #NE
dict[1.4] = '22'  #NNE
dict[1.8] = '180' #South
dict[2.0] = '202' #SSW
dict[2.2] = '135' #SE
dict[2.5] = '157' #SSE
dict[2.7] = '90'  #East
dict[2.8] = '67'  #ENE
dict[2.9] = '112' #ESE


while True:
     wind =round(adc.value*3.3,1)
     if not wind in volts:
          print('Unknown Value: ' +str(wind))
     else:
         time.sleep(0.1) #reduces CPU load
         print (str(wind),  (dict[(wind)]))






