<?php
require_once 'db.php'; // Import database credentials



// REWRITE THIS TO USE DAILYDATA table. Much faster


// Create a database connection
$mysqli = new mysqli($dbHost, $dbUser, $dbPass, $dbName);


// Check connection
if ($mysqli->connect_error) {
    die("Connection failed: " . $mysqli->connect_error);
}


$today =  date('Y-m-d', time());
list($year, $month, $day) = explode('-', $today);


// Calculate the SUM of rain_count by month for the previous 12 months
//$prev12MonthsQuery = "SELECT month, SUM(rain_count) as sum_rain_year FROM weatherdata WHERE year >= YEAR(NOW()) - 1 GROUP BY month";
//A special thanks to Googe's Bard for this one. My SQL Foo is good, but this was next level.
$prev12MonthsQuery = "SELECT CONCAT(YEAR(STR_TO_DATE(LEFT(iso_date, 6), '%Y%m')), '.', LPAD(month, 2, '0')) AS month_year,   SUM(rain_count) AS sum_rain_year FROM weather.weatherdata WHERE STR_TO_DATE(LEFT(iso_date, 6), '%Y%m') >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH) GROUP BY month_year ORDER BY month_year ASC";
$sumRainPrev12Months = $mysqli->query($prev12MonthsQuery)->fetch_all(MYSQLI_ASSOC);

$sumRainPrev12Months = $mysqli->query($prev12MonthsQuery)->fetch_all(MYSQLI_ASSOC);



header('Content-Type: application/json');
echo json_encode($sumRainPrev12Months);
