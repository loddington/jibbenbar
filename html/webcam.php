<?php
// Define the directory to search for images
$directory = "webcam/";

// Get all files in the directory
$files = glob($directory . "*.{jpg,png,gif}", GLOB_BRACE);

// Sort files by modification time in descending order
array_multisort(array_map('filemtime', $files), SORT_DESC, $files);

// Get the newest image file
$newestImage = $files ? $files[0] : '';

// Check if the newest image file exists
if (file_exists($newestImage)) {
    // Get the timestamp of the newest image file
    $timestamp = filemtime($newestImage);
    
    // Generate a unique URL for the image by appending timestamp
    $imageUrl = $newestImage . '?' . $timestamp;
    
    // Display the newest image
    echo '<img src="' . $imageUrl . '" id="newestImage" alt="Jibbenbar Weather">';
} else {
    echo 'No image found.';
}
?>
