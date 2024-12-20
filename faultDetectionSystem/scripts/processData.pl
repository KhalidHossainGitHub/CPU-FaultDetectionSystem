#!/usr/bin/perl
use strict;
use warnings;
use File::Path qw(make_path);

# Function to log errors and print to the terminal
sub log_error {
    my ($message) = @_;
    my $error_log = "../logs/error.log";
    open(my $err_log, '>>', $error_log) or die "Critical Error: Cannot open $error_log: $!";
    my $timestamp = get_timestamp();
    print $err_log "$timestamp $message\n";
    close($err_log);

    # Print the error message to the terminal
    print STDERR "$timestamp $message\n";
}

# Function to log system messages
sub log_system {
    my ($message) = @_;
    my $system_log = "../logs/system.log";
    open(my $sys_log, '>>', $system_log) or die "Critical Error: Cannot open $system_log: $!";
    my $timestamp = get_timestamp();
    print $sys_log "$timestamp $message\n";
    close($sys_log);

    # Optionally, print system messages to terminal for visibility
    #print "$timestamp $message\n";
}

# Function to get the current timestamp
sub get_timestamp {
    my @months = qw(Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec);
    my @days = qw(Sun Mon Tue Wed Thu Fri Sat);
    my ($sec, $min, $hour, $mday, $mon, $year, $wday) = localtime();
    return sprintf(
        "[%s %s %02d %02d:%02d:%02d %d]",
        $days[$wday], $months[$mon], $mday, $hour, $min, $sec, $year + 1900
    );
}

# File paths
my $raw_data_path = "../data/rawData.txt";
my $processed_data_path = "../data/processedData.csv";

# Ensure directories and logs exist
eval {
    my $processed_dir = "../data";
    unless (-d $processed_dir) {
        make_path($processed_dir) or die "Error: Could not create directory $processed_dir.";
    }
    log_system("Ensured processed data directory exists.");
};
if ($@) {
    log_error($@);
    exit 1;
}

# Create or clear the processed data file and write the header
eval {
    open(my $csv, '>', $processed_data_path) or die "Error: Could not create $processed_data_path.";
    print $csv "Timestamp,CPU Usage (%),Fault (1 or 0)\n";
    close($csv);
    log_system("Created processed data file with header.");
};
if ($@) {
    log_error($@);
    exit 1;
}

# Check if the raw data file exists and is not empty
eval {
    unless (-e $raw_data_path) {
        die "Error: The raw data file '$raw_data_path' does not exist.";
    }
    open(my $raw_file, '<', $raw_data_path) or die "Error: Could not open '$raw_data_path'.";
    my @raw_lines = <$raw_file>;
    close($raw_file);
    die "Error: The raw data file '$raw_data_path' is empty." if scalar @raw_lines == 0;
    log_system("Validated raw data file exists and is not empty.");
};
if ($@) {
    log_error($@);
    exit 1;
}

# Process the raw data
eval {
    open(my $csv_file, '>>', $processed_data_path) or die "Error: Could not open '$processed_data_path'.";
    open(my $raw_file, '<', $raw_data_path) or die "Error: Could not open '$raw_data_path'.";
    while (my $line = <$raw_file>) {
        chomp $line;
        my @parts = split /, /, $line;
        if (scalar @parts != 3) {
            log_system("Skipping invalid line: '$line'. Expected 3 parts.");
            next;
        }
        my ($timestamp, $cpu_usage, $fault) = @parts;
        if ($cpu_usage !~ /^\d+(\.\d+)?$/ || $fault !~ /^[01]$/) {
            log_system("Skipping invalid line: '$line'. Invalid CPU usage or fault value.");
            next;
        }
        $cpu_usage = sprintf("%.1f", $cpu_usage);  # Ensure one decimal place
        print $csv_file "$timestamp,$cpu_usage,$fault\n";
    }
    close($raw_file);
    close($csv_file);
    log_system("Processed data saved to $processed_data_path.");
};
if ($@) {
    log_error($@);
    exit 1;
}

# Run the modelTraining.py script if successful
eval {
    log_system("Running modelTraining.py in the background.");
    system("python3 modelTraining.py &");
};
if ($@) {
    log_error("Error: Failed to execute modelTraining.py.");
    exit 1;
}

exit 0;
