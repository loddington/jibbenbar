<?php
require_once 'db.php'; // Import database credentials


// Create a database connection
$mysqli = new mysqli($dbHost, $dbUser, $dbPass, $dbName);

// Check connection
if ($mysqli->connect_error) {
    die("Connection failed: " . $mysqli->connect_error);
}

date_default_timezone_set($station_timezone);

$today =  date('Y-m-d', time());
list($year, $month, $day) = explode('-', $today);


// Environment Sensors since midnight Temperature, Dew Point, Humidty, Preassure 
$todaysGraphDataQuery = "SELECT probe_temp, barometric_pressure, dew_point, rain_count, humidity, hour_min FROM weatherdata WHERE $year AND month = $month AND day_of_month = $day";
$todaysGraphData =  $mysqli->query($todaysGraphDataQuery)->fetch_all(MYSQLI_ASSOC);



header('Content-Type: application/json');


echo json_encode($todaysGraphData);
