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
$sumRainSinceMidnightResult = $sumRainSinceMidnight['sum_rain_today'];


//Min and Max temperatures today and the time they occured.
$minMaxTempSinceMidnightQuery = "SELECT probe_temp AS min_temp, (SELECT MAX(probe_temp) FROM weatherdata WHERE year = $year AND month = $month AND day_of_month = $day) AS max_temp, (SELECT hour_min FROM weatherdata WHERE probe_temp = min_temp AND year = $year AND month = $month AND day_of_month = $day LIMIT 1) AS min_temp_time, (SELECT hour_min FROM weatherdata WHERE probe_temp = max_temp AND year = $year AND month = $month AND day_of_month = $day LIMIT 1) AS max_temp_time FROM weatherdata WHERE year = $year AND month = $month AND day_of_month = $day GROUP BY probe_temp LIMIT 1";
$minMaxTempSinceMidnight = $mysqli->query($minMaxTempSinceMidnightQuery)->fetch_assoc();


//Min and Max temperatures this year and the day they occured. When time permits I will rewrite this query for the previous 12 months instead of this year. Its a bit useless in January.
$minMaxTempYearQuery = "SELECT mintemp AS min_temp_year, (SELECT MAX(maxtemp) FROM dailydata WHERE year =$year) AS max_temp_year, (SELECT mintemptime FROM dailydata WHERE mintemp = min_temp_year AND year = $year LIMIT 1) AS min_temp_date, (SELECT maxtemptime FROM dailydata WHERE maxtemp = max_temp_year AND year = $year LIMIT 1) AS max_temp_date FROM dailydata WHERE year = $year GROUP BY mintemp LIMIT 1";
$minMaxTempYearResult = $mysqli->query($minMaxTempYearQuery)->fetch_assoc();

$minTempYear = $minMaxTempYearResult['min_temp_year'];
$maxTempYear = $minMaxTempYearResult['max_temp_year'];
$minTempYearDate = $minMaxTempYearResult['min_temp_date'];
$maxTempYearDate = $minMaxTempYearResult['max_temp_date'];


$datetime = new DateTime('@' . $minTempYearDate);
$datetime->setTimezone(new DateTimeZone($station_timezone));
$minTempYearDate_human = $datetime->format('g:ia jS D M Y');

$datetime = new DateTime('@' . $maxTempYearDate);
$datetime->setTimezone(new DateTimeZone($station_timezone));
$maxTempYearDate_human = $datetime->format('g:ia jS D M Y');



$minMaxTempYearArray = array(
    'max_temp_year' => "$maxTempYear",
    'max_temp_date' => $maxTempYearDate_human,
    'min_temp_year' => "$minTempYear",
    'min_temp_date' => $minTempYearDate_human
);



//Rain count total this month
//$sumRainSinceFirstofMonthQuery = "SELECT SUM(sumrain) as sum_rain_month FROM dailydata WHERE year = $year AND month = $month";
//$sumRainSinceFirstofMonth = $mysqli->query($sumRainSinceFirstofMonthQuery)->fetch_assoc();


$query_weatherdata = "SELECT SUM(rain_count) AS total_rain_count FROM weatherdata WHERE month = $month AND year = $year AND day_of_month = $day";
$query_dailydata = "SELECT SUM(sumrain) AS total_sumrain FROM dailydata WHERE month  = $month AND year = $year";
$result_weatherdata = $mysqli->query($query_weatherdata);
$result_dailydata = $mysqli->query($query_dailydata);
if ($result_weatherdata && $result_dailydata) {
    // Fetch the results
    $row_weatherdata = mysqli_fetch_assoc($result_weatherdata);
    $row_dailydata = mysqli_fetch_assoc($result_dailydata);

    // Get the sum values
    $total_rain_count = $row_weatherdata['total_rain_count'];
    $total_sumrain = $row_dailydata['total_sumrain'];

    // Combine the results
    $combined_sum = $total_rain_count + $total_sumrain;

    // Output the combined sum
    //echo "Combined Sum: " . $combined_sum;

    $sumRainSinceFirstofMonth = array(
    'sum_rain_month' => $combined_sum
    );

} else {
    // Handle errors for the first of the month.

   $sumRainSinceFirstofMonth = array(
   'sum_rain_month' => $total_rain_count
   );

}






//Rain Yesterday
$YesterdayRainQuery = "SELECT sumrain as rain_yesterday from dailydata ORDER BY epoch DESC LIMIT 1";
$YesterdayRain =  $mysqli->query($YesterdayRainQuery)->fetch_assoc();



//Last Month total Rain
$prevMonth = date('Y-m-d 00:00:00', strtotime('first day of last month'));
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


// Convert Epoch to human readable time. include time zone.
$EpochQuery = "SELECT epoch FROM weatherdata ORDER BY epoch DESC LIMIT 1";
$EpochResultRaw = $mysqli->query($EpochQuery)->fetch_assoc();
$EpochResult = round(implode(" ",$EpochResultRaw), 1);

$epoch = $EpochResult;

// Create a DateTime object with the given epoch timestamp in UTC timezone
$dateTime = new DateTime("@$epoch");
$dateTime->setTimezone(new DateTimeZone($station_timezone));

// Format the datetime object into the desired format
$dateString = $dateTime->format('g:ia jS F Y');

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



// Get the latest values for temperature, humidity, and wind speed for the Apparent Temperature calculation. Apparent Temperature is often called "Feels Like". 
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


// Query to find the row with maximum sumrain - Wettest Day of the year.
$maxsumrainsql = "SELECT epoch, sumrain FROM dailydata WHERE sumrain = (SELECT MAX(sumrain) FROM (SELECT sumrain FROM dailydata ORDER BY epoch DESC LIMIT 365) AS last365)";
$maxsumrainresult =  $mysqli->query($maxsumrainsql)->fetch_assoc();

$maxsumrain = $maxsumrainresult['sumrain'];
$maxsumraindate = $maxsumrainresult['epoch'];
 

$datetime = new DateTime('@' . $maxsumraindate);
$datetime->setTimezone(new DateTimeZone($station_timezone));
$human_readable_date = $datetime->format('jS D F Y');


$maxsumrainsArray = array(
    'max_sumrain' => "$maxsumrain",
    'max_sumrain_date' => $human_readable_date
);





//SunRise and SunSet calcs
//instead of date_sun_info look at https://github.com/gregseth/suncalc-php to get moon too.
$date = new DateTime();
$timestamp = $date->getTimestamp();

$info = date_sun_info($timestamp, $latitude, $longitude);


$sunrise = array(
   'sunrise' => Date('g:ia', $info['sunrise']),
 );

$sunset = array(
   'sunset' => Date('g:ia', $info['sunset']),
 );

$zenith = array(
   'zenith' => Date('g:ia', $info['transit']),
 );

$civil_twilight_end = array(
   'civil_twilight_end' => Date('g:ia', $info['civil_twilight_end']),
 );


$astronomical_twilight_begin = array(
   'astronomical_twilight_begin' => Date('g:ia', $info['astronomical_twilight_begin']),
 );

$astronomical_twilight_end = array(
   'astronomical_twilight_end' => Date('g:ia', $info['astronomical_twilight_end']),
 );


$civil_twilight_begin = array(
   'civil_twilight_begin' => Date('g:ia', $info['civil_twilight_begin']),
 );



// End SunRise and SunSet Calcs


$webcam_image_file = "<img src=/webcam/jibbenbar.jpg alt=jibbenbar_Weather width=100%>";

$webcamImageArray = array(
    'webcam_image' => "$webcam_image_file"
);




//$FirstEpochQuery = "SELECT epoch FROM dailydata AS firstepoch limit 1";
$FirstEpochQuery = "SELECT epoch FROM dailydata limit 1";
$FirstEpochQueryResult =  $mysqli->query($FirstEpochQuery)->fetch_assoc();

$first_epoch = $FirstEpochQueryResult['epoch'];

$datetime = new DateTime('@' . $first_epoch);
$datetime->setTimezone(new DateTimeZone($station_timezone));
$human_readable_date = $datetime->format('jS F Y');


$FirstEpochQueryArray = array(
    'first_epoch' => "$human_readable_date"
);




// Combine data and output JSON

$combinedData = array_merge($PageTitle, $latestResult, $sumRainSinceMidnight, $sumRainSinceFirstofMonth, $sumRainLastMonth, $minMaxTempSinceMidnight, $sunrise, $sunset, $ApparentTemperatureyArray, $barometricComparisonArray, $compassPointArray, $latestEpochResult, $minMaxTempYearArray, $zenith, $civil_twilight_end, $astronomical_twilight_begin, $astronomical_twilight_end, $civil_twilight_begin, $maxsumrainsArray, $YesterdayRain, $webcamImageArray, $FirstEpochQueryArray);

header('Content-Type: application/json');
echo json_encode($combinedData);
