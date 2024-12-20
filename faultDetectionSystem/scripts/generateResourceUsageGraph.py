import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import sys
from datetime import datetime

# Define file paths
processed_data_path = os.path.expanduser("../data/processedData.csv")
output_graph_path = os.path.expanduser("../data/resourceUsageGraph.png")
system_log_path = os.path.expanduser("../logs/system.log")
error_log_path = os.path.expanduser("../logs/error.log")


def log_message(log_path, message):
    """Log messages to the specified file with a timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, 'a') as log_file:
        log_file.write(f"[{timestamp}] {message}\n")


def log_and_print_error(message):
    """Log errors to the error log and display them in the terminal."""
    log_message(error_log_path, message)
    print(f"Error: {message}", file=sys.stderr)


try:
    # Check if processed data file exists
    if not os.path.exists(processed_data_path):
        raise FileNotFoundError(f"Processed data file not found: {processed_data_path}")

    # Read data from CSV
    with open(processed_data_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        header = next(csvreader)  # Skip header
        data = [row for row in csvreader]

    # If the data is empty, raise an exception
    if not data:
        raise ValueError("No data found in the processedData.csv file.")

    # Prepare data for logistic regression
    timestamps = [row[0] for row in data]
    cpu_usage = np.array([float(row[1]) for row in data]).reshape(-1, 1)  # CPU usage as feature
    faults = np.array([int(row[2]) for row in data])  # Fault (1) or Non-fault (0)

    # Standardize the CPU usage values (important for logistic regression)
    scaler = StandardScaler()
    cpu_usage_scaled = scaler.fit_transform(cpu_usage)

    # Create and fit the logistic regression model
    model = LogisticRegression()
    model.fit(cpu_usage_scaled, faults)

    # Generate predicted values from the model
    predictions = model.predict(cpu_usage_scaled)

    # Plotting the data
    plt.figure(figsize=(10, 6))

    # Scatter plot for CPU usage vs. Fault (1 or 0)
    plt.scatter(cpu_usage, faults, color='blue', label='Data points', alpha=0.6)

    # Plot the logistic regression curve (sigmoid curve)
    x_range = np.linspace(min(cpu_usage_scaled), max(cpu_usage_scaled), 500)
    y_range = model.predict_proba(x_range.reshape(-1, 1))[:, 1]
    plt.plot(scaler.inverse_transform(x_range.reshape(-1, 1)), y_range, color='red', linewidth=2, label='Logistic Regression Curve')

    # Labeling
    plt.title('CPU Usage vs Fault Detection (Logistic Regression)', fontsize=16)
    plt.xlabel('CPU Usage (%)')
    plt.ylabel('Fault (1) / Non-Fault (0)')
    plt.legend()

    # Save the plot to the file
    plt.savefig(output_graph_path)
    log_message(system_log_path, f"Graph saved successfully at {output_graph_path}")
    plt.close()

    # Print instructions to the terminal
    instructions = (
        "To run the fault prediction program, use:\n"
        "   python faultPrediction.py &\n"
        "To view logs, navigate to ../logs and use commands like:\n"
        "   cat, head (first 10 lines), or tail (last 10 lines) with system.log or error.log\n"
        "To view data files, navigate to ../data and use:\n"
        "   cat rawData.txt\n"
        "   cat processedData.csv\n"
        "To view the logistic regression graph, use:\n"
        "   xdg-open resourceUsageGraph.png\n"
    )
    print(instructions)

except FileNotFoundError as fnf_error:
    log_and_print_error(f"FileNotFoundError: {fnf_error}")
    sys.exit(1)
except ValueError as val_error:
    log_and_print_error(f"ValueError: {val_error}")
    sys.exit(1)
except PermissionError as perm_error:
    log_and_print_error(f"Permission denied when accessing files: {perm_error}")
    sys.exit(1)
except Exception as e:
    log_and_print_error(f"An unexpected error occurred: {e}")
    sys.exit(1)
