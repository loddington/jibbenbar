<?php

require_once 'db.php'; // Import database credentials


// Create a database connection
$mysqli = new mysqli($dbHost, $dbUser, $dbPass, $dbName);

// Check connection
if ($mysqli->connect_error) {
    die("Connection failed: " . $mysqli->connect_error);
}


$PageTitle = array(
    'PageHeading' => "$sitename"
);


//Date definition of today, year, month and day
date_default_timezone_set($station_timezone);
$today =  date('Y-m-d', time());
list($year, $month, $day) = explode('-', $today);


// Get the latest result
$latestResultQuery = "SELECT * FROM weatherdata  ORDER BY year DESC, month DESC, day_of_month DESC, hour_min DESC LIMIT 1";
$latestResult = $mysqli->query($latestResultQuery)->fetch_assoc();


//Rain Today & Average Temp
$sumRainSinceMidnightQuery = "SELECT ROUND(AVG(probe_temp) ,1) as avg_temp, SUM(rain_count) as sum_rain_today FROM weatherdata WHERE year = $year AND month = $month AND day_of_month = $day";
$sumRainSinceMidnight = $mysqli->query($sumRainSinceMidnightQuery)->fetch_assoc();


//Min and Max temperatures today and the time they occured.
$minMaxTempSinceMidnightQuery = "SELECT probe_temp AS min_temp, (SELECT MAX(probe_temp) FROM weatherdata WHERE year = $year AND month = $month AND day_of_month = $day) AS max_temp, (SELECT hour_min FROM weatherdata WHERE probe_temp = min_temp AND year = $year AND month = $month AND day_of_month = $day LIMIT 1) AS min_temp_time, (SELECT hour_min FROM weatherdata WHERE probe_temp = max_temp AND year = $year AND month = $month AND day_of_month = $day LIMIT 1) AS max_temp_time FROM weatherdata WHERE year = $year AND month = $month AND day_of_month = $day GROUP BY probe_temp LIMIT 1";
$minMaxTempSinceMidnight = $mysqli->query($minMaxTempSinceMidnightQuery)->fetch_assoc();


//Min and Max temperatures this year and the day they occured. When time permits I will rewrite this query for the previous 12 months instead of this year. Its a bit useless in January.
$minMaxTempYearQuery = "SELECT probe_temp AS min_temp_year, (SELECT MAX(probe_temp) FROM weatherdata WHERE year =$year) AS max_temp_year, (SELECT ISO_DATE FROM weatherdata WHERE probe_temp = min_temp_year AND year = $year LIMIT 1) AS min_temp_date, (SELECT ISO_DATE FROM weatherdata WHERE probe_temp = max_temp_year AND year = $year LIMIT 1) AS max_temp_date FROM weatherdata WHERE year = $year GROUP BY probe_temp LIMIT 1";
$minMaxTempYear = $mysqli->query($minMaxTempYearQuery)->fetch_assoc();


//Rain count total this month
$sumRainSinceFirstofMonthQuery = "SELECT SUM(rain_count) as sum_rain_month FROM weatherdata WHERE year = $year AND month = $month";
$sumRainSinceFirstofMonth = $mysqli->query($sumRainSinceFirstofMonthQuery)->fetch_assoc();


//Last Month total Rain
$prevMonth = date('Y-m-d 00:00:00', strtotime('first day of last month'));
//$sumRainLastMonthQuery = "SELECT SUM(rain_count) as sum_rain_last_month FROM weatherdata WHERE year = YEAR('$prevMonth') AND month = MONTH('$prevMonth')";
//$sumRainLastMonth = $mysqli->query($sumRainLastMonthQuery)->fetch_assoc();
$sumRainLastMonthQuery = "SELECT SUM(sumrain) as sum_rain_last_month FROM dailydata WHERE year = YEAR('$prevMonth') AND month = MONTH('$prevMonth')";
$sumRainLastMonth = $mysqli->query($sumRainLastMonthQuery)->fetch_assoc();


//Compass degrees to cardinal compas points. ie 0 equals North. 90 equals South. 
$latestWindQuery = "SELECT wind_direction FROM weatherdata as wind_degrees ORDER BY year DESC, month DESC, day_of_month DESC, hour_min DESC LIMIT 1";
$latestWindResultRaw = $mysqli->query($latestWindQuery)->fetch_assoc();
$latestWindResult =  round(implode(" ",$latestWindResultRaw), 1);



function degreesToCompass($degrees) {
//    $cardinalDirections = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N'];
    $cardinalDirections = ['North', 'NNE', 'North East', 'ENE', 'East', 'ESE', 'South East', 'SSE', 'South', 'SSW', 'South West', 'WSW', 'West', 'WNW', 'North West', 'NNW',];

    // Calculate the index based on 22.5 degree segments because we store the wind direction by degrees 0,22.5,45,67.5,90,112.5,180 etc
    $index = round($degrees / 22.5);

    // Return the cardinal direction
    return $cardinalDirections[$index];
}

$compassPoint = degreesToCompass($latestWindResult);


$compassPointArray = array(
    'compass_point' => $compassPoint
);




// This requires the database to have timezonedata - I'll just do it by hand instead.
//$latestEpochQuery = "SELECT DATE_FORMAT(CONVERT_TZ(FROM_UNIXTIME(epoch), 'UTC', 'Australia/Brisbane'), '%h:%i%p %D %M %Y') AS human_time FROM weatherdata ORDER BY epoch DESC LIMIT 1";
//$latestEpochResult = $mysqli->query($latestEpochQuery)->fetch_assoc();


// Convert Epoch to human readable time. include time zone.
$EpochQuery = "SELECT epoch FROM weatherdata ORDER BY epoch DESC LIMIT 1";
$EpochResultRaw = $mysqli->query($EpochQuery)->fetch_assoc();
$EpochResult = round(implode(" ",$EpochResultRaw), 1);

$epoch = $EpochResult;

// Create a DateTime object with the given epoch timestamp in UTC timezone
$dateTime = new DateTime("@$epoch");
$dateTime->setTimezone(new DateTimeZone($station_timezone));

// Format the datetime object into the desired format
$dateString = $dateTime->format('h:iA jS F Y');

//echo $dateString;

$latestEpochResult = array(
    'human_time' => "$dateString"
);



 

// Fetch the last 6 values of barometric_pressure so we can perform some statistical analysys
$lastBarometricValuesQuery = "SELECT barometric_pressure FROM weatherdata WHERE barometric_pressure IS NOT NULL ORDER BY year DESC, month DESC, day_of_month DESC, hour_min DESC LIMIT 6";
$lastBarometricValuesResult = $mysqli->query($lastBarometricValuesQuery);

// Extract values into an array
$lastBarometricValues = [];
while ($row = $lastBarometricValuesResult->fetch_assoc()) {
    $lastBarometricValues[] = $row['barometric_pressure'];
}

// Calculate the average manually
$averageBarometric = count($lastBarometricValues) > 0 ? array_sum($lastBarometricValues) / count($lastBarometricValues) : 0;


// Get the latest value of barometric_pressure
$latestBarometricQuery = "SELECT barometric_pressure FROM weatherdata ORDER BY year DESC, month DESC, day_of_month DESC, hour_min DESC LIMIT 1";
$latestBarometricValue = $mysqli->query($latestBarometricQuery)->fetch_assoc()['barometric_pressure'];


//Amount from the average the result has to be before it isn't considered steady.
$tolerance = 0.015; // 0.015% tolerance - Feel free to adjust

$lowerTolerance = $averageBarometric * (1 - $tolerance / 100);
$upperTolerance = $averageBarometric * (1 + $tolerance / 100);

$barometricComparison = '';

if ($latestBarometricValue > $upperTolerance) {
    $barometricComparison = 'rising';
} elseif ($latestBarometricValue < $lowerTolerance) {
    $barometricComparison = 'dropping';
} else {
    $barometricComparison = 'steady';
}


$barometricComparisonArray = array(
    'barometricComparison' => $barometricComparison
);


// Print debugging information
//echo "Latest Barometric Value: " . $latestBarometricValue . "<br>";
//echo "Average Barometric Value: " . $averageBarometric . "<br>";
//echo "Lower Tolerance: " . $lowerTolerance . "<br>";
//echo "Upper Tolerance: " . $upperTolerance . "<br>";
//echo "Barometric Comparison: " . $barometricComparison . "<br>";



// Get the latest values for temperature, humidity, and wind speed for the Apparent Temperature calculation. Apparent Temperature is often called Feels Like. 
$latestWeatherQuery = "SELECT probe_temp, humidity, wind_speed FROM weatherdata ORDER BY year DESC, month DESC, day_of_month DESC, hour_min DESC LIMIT 1";
$latestWeatherData = $mysqli->query($latestWeatherQuery)->fetch_assoc();

$latestTemperature = $latestWeatherData['probe_temp'];
$latestHumidity = $latestWeatherData['humidity'];
$latestWindSpeed = $latestWeatherData['wind_speed'];

// Calculate the Australian apparent temperature - The Math varies around the world. This one takes wind speed into consideration too.

$ApparentTemperature = calculateApparentTemperature($latestTemperature, $latestHumidity, $latestWindSpeed);

function calculateApparentTemperature($temperature, $humidity, $windSpeed)
{
    // Calculate water vapor pressure in hPa
    $P = ($humidity / 100) * 6.105 * exp((17.27 * $temperature) / (237.7 + $temperature));

    // Calculate Australian apparent temperature
    $ApparentTemperature = $temperature + 0.33 * $P - 0.7 * $windSpeed - 4;

    return round($ApparentTemperature,1);
}



$ApparentTemperatureyArray = array(
    'FeelsLike' => "$ApparentTemperature"
);


//SunRise and SunSet calcs
//instead of date_sun_info look at https://github.com/gregseth/suncalc-php to get moon too.
$date = new DateTime();
$timestamp = $date->getTimestamp();

$info = date_sun_info($timestamp, $latitude, $longitude);


$sunrise = array(
   'sunrise' => Date('H:i', $info['sunrise']),
 );

$sunset = array(
   'sunset' => Date('H:i', $info['sunset']),
 );

$zenith = array(
   'zenith' => Date('H:i', $info['transit']),
 );

$civil_twilight_end = array(
   'civil_twilight_end' => Date('H:i', $info['civil_twilight_end']),
 );


$astronomical_twilight_begin = array(
   'astronomical_twilight_begin' => Date('H:i', $info['astronomical_twilight_begin']),
 );

$astronomical_twilight_end = array(
   'astronomical_twilight_end' => Date('H:i', $info['astronomical_twilight_end']),
 );


$civil_twilight_begin = array(
   'civil_twilight_begin' => Date('H:i', $info['civil_twilight_begin']),
 );



// End SunRise and SunSet Calcs



// Combine data and output JSON

$combinedData = array_merge($PageTitle,$latestResult, $sumRainSinceMidnight, $sumRainSinceFirstofMonth, $sumRainLastMonth, $minMaxTempSinceMidnight, $sunrise, $sunset, $ApparentTemperatureyArray, $barometricComparisonArray, $compassPointArray, $latestEpochResult, $minMaxTempYear, $zenith, $civil_twilight_end, $astronomical_twilight_begin, $astronomical_twilight_end, $civil_twilight_begin );

header('Content-Type: application/json');
echo json_encode($combinedData);
