<?php
$dbHost = "127.0.0.1";
$dbUser = "wuser";
$dbPass = "YourReadWritePasswordHere";
$dbName = "weather";



//Set to your local time zone - Nothing to do with the DB connection but helpful!
date_default_timezone_set('Australia/Brisbane');


//The database table  definition.


/*
CREATE TABLE weatherdata (
  epoch INT PRIMARY KEY,
  iso_date bigint,
  hour_min decimal(4,2),
  day_of_month tinyint,
  month tinyint,
  year mediumint,
  backup_temp decimal(5,2),
  barometric_preassure decimal(6,2),
  humidity decimal(5,2),
  probe_temp decimal(5,2),
  dew_point decimal(4,2),
  rain_count decimal(5,2),
  wind_speed decimal(5,2),
  wind_gusts decimal(5,2),
  wind_direction mediumint,
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
  wind_direction_frequency mediumint,
  max_wind decimal(5,2),
  max_barometer decimal(6,2),
  min_barometer decimal(6,2),
  max_sun_temp decimal(5,2),
  avg_sun_temp decimal(5,2),
  min_sun_temp decimal(5,2)
 );

*/




?>
