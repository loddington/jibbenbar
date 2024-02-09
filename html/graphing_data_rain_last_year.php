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


// Calculate the SUM of rain_count by month for the previous 12 months
// complicated by me wanting to conncatinate the year and month
$prev12MonthsQuery = "SELECT CONCAT(YEAR(STR_TO_DATE(LEFT(iso_date, 6), '%Y%m')), '.', LPAD(month, 2, '0')) AS month_year,   
                      SUM(sumrain) AS sum_rain_year FROM weather.dailydata WHERE STR_TO_DATE(LEFT(iso_date, 6), '%Y%m') >= DATE_SUB(CURDATE(), 
                      INTERVAL 12 MONTH) GROUP BY month_year ORDER BY month_year ASC";
$sumRainPrev12Months = $mysqli->query($prev12MonthsQuery)->fetch_all(MYSQLI_ASSOC);


header('Content-Type: application/json');
echo json_encode($sumRainPrev12Months);
