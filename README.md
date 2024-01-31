Jibbenbar RaspBerry Pi Weather Station.

I'll put together some real install instructions. 

https://downloads.raspberrypi.com/raspios_arm64/images/raspios_arm64-2023-12-06/2023-12-05-raspios-bookworm-arm64.img.xz


 rasp-config -> interface options -> SPI I2C and 1-Wire
 
 apt update
 apt upgrade 
 apt install mariadb-server mycli mariadb-backup
 sudo systemctl enable mariadb
 mariadb
 create database weather;
 GRANT ALL privileges on weather.* TO 'wuser'@'localhost' identified by 'YourReadWritePasswordHere';
 GRANT SELECT ON weather.* TO 'frontend'@'localhost' IDENTIFIED BY 'YourReadOnlyPasswordHere';
 use weather
 
 

 
CREATE TABLE weatherdata (
  epoch INT PRIMARY KEY,
  iso_date bigint,
  hour_min decimal(4,2),
  day_of_month tinyint,
  month tinyint,
  year mediumint,
  backup_temp decimal(5,2),
  barometric_pressure decimal(6,2),
  humidity decimal(5,2),
  probe_temp decimal(5,2),
  dew_point decimal(4,2),
  rain_count decimal(5,2),
  wind_speed decimal(5,2),
  wind_gusts decimal(5,2),
  wind_direction decimal(4,1),
  LUX int,
  UV decimal(3,1),
  sun_temp decimal(5,2)
 );


CREATE TABLE dailydata (
  epoch INT PRIMARY KEY,
  iso_date bigint,
  day_of_month tinyint,
  month tinyint,
  year mediumint,
  week tinyint,
  avgtemp decimal(5,2),
  maxtemp decimal(5,2),
  mintemp decimal(5,2),
  avgdew decimal(5,2),
  sumrain decimal(5,2),
  avgbarometric decimal(6,2),
  avghumidity decimal(5,2),
  avgwind decimal(5,2),
  avglux int,
  luxhours decimal(4,2),
  avguv decimal(3,2),
  sumluxday int,
  sumuvday decimal(5,2),
  windhours decimal(5,2),
  maxtemptime decimal(4,2),
  mintemptime decimal(4,2),
  wind_direction_frequency decimal(4,1),
  max_wind decimal(5,2),
  max_barometer decimal(6,2),
  min_barometer decimal(6,2),
  max_sun_temp decimal(5,2),
  avg_sun_temp decimal(5,2),
  min_sun_temp decimal(5,2)
 );


 apt install apache2 php php-json php-cli libnet-address-ip-local-perl php-mysql python3-smbus2 python3-gpiozero python3-flask-api libmariadbd-dev
 sudo systemctl enable --now apache2
 service mariadb start
 
 


pip3 install RPi.bme280  Adafruit_CircuitPython_AHTx0 --break-system-packages
pip install mariadb  --break-system-packages



curl  -H "Content-Type: application/json"  -X GET http://localhost:5000/sensors/bucket_tips
curl -d '{"id":"bucket_tips","sensor_value":"0"}' -H "Content-Type: application/json" -X PUT http://localhost:5000/sensors/bucket_tips
curl -d '{"id":"bucket_tips"}' -H "Content-Type: application/json" -X PUT http://localhost:5000/sensors/bucket_tips/increment 
 
 

cp /var/www/jibbenbar/systemdfiles/wind.service /etc/systemd/system/wind.service

systemctl enable rainfall
systemctl enable flask-data-logger-api
systemctl enable wind


