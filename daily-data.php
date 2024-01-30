<?php
require_once 'db-rw.php'; // Import database credentials

// I started to get nerveous about database load from queries and DB size, so I decided to create a new table (dailydata) that contains some statistics of each days data on 1 line.  
// This will also help in the future if we want to start purging the older data from weatherdata. I can't see needing more than 60 days of full data. 

// Run this at 11.58pm from a cron job. 

// This file should not be accessible via a web browser

// Create a database connection
$mysqli = new mysqli($dbHost, $dbUser, $dbPass, $dbName);

// Check connection
if ($mysqli->connect_error) {
    die("Connection failed: " . $mysqli->connect_error);
}



// Yes, I've added week. I know, I could get this from epoch, but this is simpler and less intensive
$today =  date('Y-m-d-W', time());
list($year, $month, $day, $week) = explode('-', $today);


// luxhours - For me, this is all about solar generation, I'd like to put some sort of measurement on it. 
// So, how many hours of sunlight over X Lux did we have today? Full sunlight is 120,000. Count how many lines where LUX is greater than say 80K? 

$luxthreshold = '80000'; // A guestimate at best, needs some calibration. 
$windthreshold = '5'; // 5km/h wind ? I dont know, I dont do wind power generation.
// I'm using 0.166667 in SUM(CASE WHEN light_meter > $luxthreshold THEN 0.166667 ELSE 0 END) AS luxhours because we take 6 readings an hour.  If you do more (or less) then you will need to change this.



//Min and Max temperatures today and the time they occured.
$minMaxTempSinceMidnightQuery = "SELECT probe_temp AS min_temp, (SELECT MAX(probe_temp) FROM weatherdata WHERE year = $year AND month = $month AND day_of_month = $day) AS max_temp, (SELECT hour_min FROM weatherdata WHERE probe_temp = min_temp AND year = $year AND month = $month AND day_of_month = $day LIMIT 1) AS min_temp_time, (SELECT hour_min FROM weatherdata WHERE probe_temp = max_temp AND year = $year AND month = $month AND day_of_month = $day LIMIT 1) AS max_temp_time FROM weatherdata WHERE year = $year AND month = $month AND day_of_month = $day GROUP BY probe_temp LIMIT 1";
$minMaxTempSinceMidnightresult = $mysqli->query($minMaxTempSinceMidnightQuery)->fetch_assoc();
$mintemp = $minMaxTempSinceMidnightresult['min_temp'];
$maxtemp = $minMaxTempSinceMidnightresult['max_temp'];
$maxtemptime = $minMaxTempSinceMidnightresult['max_temp_time'];
$mintemptime = $minMaxTempSinceMidnightresult['min_temp_time'];



$EndofDayWindQuery = "SELECT wind_direction,  COUNT(wind_direction) AS value_occurrence from weatherdata where year = 2024 and month = 1 and day_of_month = 15 group by wind_direction order by value_occurrence DESC limit 1";
$windresult = $mysqli->query($EndofDayWindQuery)->fetch_assoc();
$wind_direction_frequency = $windresult['wind_direction']; 


$EndofDayDataQuery = "SELECT MAX(epoch) as epoch, MAX(iso_date) as iso_date, $week as week, day_of_month, month, year, ROUND(AVG(probe_temp) ,2) as avgtemp, $maxtemp as maxtemp, $mintemp as mintemp, ROUND(AVG(dew_point) ,2) as avgdew, SUM(rain_count) as sumrain, ROUND(AVG(barometric_pressure), 2) as avgbarometric, ROUND(AVG(humidity), 2) as avghumidity, ROUND(AVG(wind_speed), 2) as avgwind, ROUND(AVG(LUX), 2) as avglux, ROUND(AVG(UV), 2) as avguv, SUM(CASE WHEN LUX > $luxthreshold THEN 0.166667 ELSE 0 END) AS luxhours, SUM(LUX) as sumluxday, SUM(UV) as sumuvday, SUM(CASE WHEN wind_speed > $windthreshold THEN 0.166667 ELSE 0 END) AS windhours, $maxtemptime as maxtemptime, $mintemptime as mintemptime, $wind_direction_frequency as wind_direction_frequency, ROUND(MAX(wind_gusts), 2) as max_wind_gust, ROUND(MAX(barometric_pressure), 2) as maxbarometer, ROUND(MIN(barometric_pressure), 2) as minbarometer, MAX(sun_temp) as max_sun_temp, AVG(sun_temp) as avg_sun_temp,  MIN(sun_temp) as min_sun_temp FROM weatherdata WHERE year = $year AND month = $month AND day_of_month = $day";
$EndofDayData =  $mysqli->query($EndofDayDataQuery)->fetch_all(MYSQLI_ASSOC);

$insertQuery = "INSERT INTO dailydata (
    epoch, iso_date, week, day_of_month, month, year,
    avgtemp, maxtemp, mintemp, avgdew, sumrain, avgbarometric,
    avghumidity, avgwind, avglux, luxhours, avguv, sumluxday, sumuvday, windhours, maxtemptime, mintemptime, wind_direction_frequency, max_wind, max_barometer, min_barometer, max_sun_temp, avg_sun_temp, min_sun_temp 
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";


$stmt = $mysqli->prepare($insertQuery);


#sanitize your inputs. You will see its all numbers and decimals.
foreach ($EndofDayData as $row) {
    $stmt->bind_param("iiiiiiddddddddddddddddidddddd",
        $row['epoch'],
        $row['iso_date'],
        $row['week'],
        $row['day_of_month'],
        $row['month'],
        $row['year'],
        $row['avgtemp'],
        $row['maxtemp'],
        $row['mintemp'],
        $row['avgdew'],
        $row['sumrain'],
        $row['avgbarometric'],
        $row['avghumidity'],
        $row['avgwind'],
        $row['avglux'],
        $row['luxhours'],
        $row['avguv'],
	$row['sumluxday'],
	$row['sumuvday'],
	$row['windhours'],
	$row['maxtemptime'],
	$row['mintemptime'],
	$row['wind_direction_frequency'],
	$row['max_wind_gust'],
	$row['maxbarometer'],
	$row['minbarometer'],
	$row['max_sun_temp'],
	$row['avg_sun_temp'],
	$row['min_sun_temp']
    );

    $stmt->execute();
}



$stmt->close();
$mysqli->close();



//header('Content-Type: application/json');

echo json_encode($EndofDayData);


