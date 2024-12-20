import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import pickle
import sys
import subprocess
import datetime

# File paths
processed_data_path = os.path.expanduser("../data/processedData.csv")
model_file_path = os.path.expanduser("../scripts/faultDetectionModel.pkl")
log_dir = os.path.expanduser("../logs")
error_log_path = os.path.join(log_dir, "error.log")
system_log_path = os.path.join(log_dir, "system.log")

# Ensure the log directory exists
os.makedirs(log_dir, exist_ok=True)

def log_message(log_path, message):
    """Logs a message to the specified log file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}\n"
    with open(log_path, "a") as log_file:
        log_file.write(formatted_message)

def log_error(message, filename):
    """Logs an error message and prints it to the terminal."""
    full_message = f"Error in {filename}: {message}"
    log_message(error_log_path, full_message)
    print(full_message, file=sys.stderr)
    sys.exit(1)

def log_system(message):
    """Logs a system message (no printing to the terminal)."""
    log_message(system_log_path, message)

try:
    # Check if the processed data file exists
    if not os.path.exists(processed_data_path):
        log_error(f"The processed data file '{processed_data_path}' does not exist.", __file__)

    # Load the processed data
    data = pd.read_csv(processed_data_path)

    # Validate data columns
    required_columns = ["Timestamp", "CPU Usage (%)", "Fault (1 or 0)"]
    if not all(col in data.columns for col in required_columns):
        log_error(f"Missing required columns in the data file. Expected: {required_columns}", __file__)

    # Extract features (CPU Usage) and target (Fault)
    X = data["CPU Usage (%)"].values.reshape(-1, 1)
    y = data["Fault (1 or 0)"].values

    # Split the data into training (80%) and testing (20%) sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train the logistic regression model
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # Test the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    # Log training results
    log_system(f"Model training complete. Accuracy: {accuracy * 100:.2f}%")
    log_system("Classification Report:")
    log_system(classification_report(y_test, y_pred, target_names=["No Fault (0)", "Fault (1)"]))

    # Save the trained model to a file
    with open(model_file_path, 'wb') as model_file:
        pickle.dump(model, model_file)
    log_system(f"Trained model has been saved to {model_file_path}")

    # Calculate and log average CPU usage for faults and non-faults
    fault_avg = data[data["Fault (1 or 0)"] == 1]["CPU Usage (%)"].mean()
    non_fault_avg = data[data["Fault (1 or 0)"] == 0]["CPU Usage (%)"].mean()
    log_system(f"Average CPU Usage for Faults (1): {fault_avg:.2f}%")
    log_system(f"Average CPU Usage for Non-Faults (0): {non_fault_avg:.2f}%")

    # Run generateResourceUsageGraph.py in the background
    subprocess.run(["python3", "../scripts/generateResourceUsageGraph.py"], check=True)
    log_system("Successfully started generateResourceUsageGraph.py in the background.")

    # Exit successfully
    sys.exit(0)

except FileNotFoundError as fnf_error:
    log_error(fnf_error, __file__)
except ValueError as val_error:
    log_error(val_error, __file__)
except PermissionError as perm_error:
    log_error(f"Permission denied when accessing files. {perm_error}", __file__)
except Exception as e:
    log_error(f"An unexpected error occurred: {e}", __file__)
