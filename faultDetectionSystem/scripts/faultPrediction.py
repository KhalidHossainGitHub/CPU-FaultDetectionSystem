import joblib
import time
from datetime import datetime
import psutil
import os
import subprocess

# Load the trained model from the .pkl file
try:
    model = joblib.load("faultDetectionModel.pkl")
except FileNotFoundError:
    log_message("../logs/error.log", "Error: The trained model file 'faultDetectionModel.pkl' was not found.")
    exit(1)
except Exception as e:
    log_message("../logs/error.log", f"Error loading model: {e}")
    exit(1)

# Paths for the log files
system_log_path = "../logs/system.log"
error_log_path = "../logs/error.log"

def log_message(log_path, message):
    """Append a message to the specified log file."""
    try:
        with open(log_path, 'a') as log_file:
            log_file.write(message + "\n")
    except Exception as e:
        print(f"Error logging to {log_path}: {e}")

def execute_subprocess(script, *args):
    """Run a subprocess and log success or failure messages."""
    try:
        result = subprocess.run([script, *args], check=True, text=True, capture_output=True)
        success_message = (
            f"[{datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}] "
            f"Subprocess '{script}' completed successfully. Output:\n{result.stdout.strip()}"
        )
        log_message(system_log_path, success_message)  # Log to system.log
    except subprocess.CalledProcessError as e:
        error_message = (
            f"[{datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}] "
            f"Subprocess '{script}' failed with return code {e.returncode}. Error Output:\n{e.stderr.strip()}"
        )
        log_message(error_log_path, error_message)  # Log to error.log
        raise  # Re-raise the exception to halt on error
    except FileNotFoundError:
        error_message = (
            f"[{datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}] "
            f"Error: Script '{script}' not found."
        )
        log_message(error_log_path, error_message)  # Log to error.log
        raise
    except Exception as e:
        error_message = (
            f"[{datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}] "
            f"Unexpected error while running subprocess '{script}': {e}"
        )
        log_message(error_log_path, error_message)  # Log to error.log
        raise

def get_cpu_usage():
    """Get the current CPU usage in percentage using psutil."""
    try:
        cpu_usage = psutil.cpu_percent(interval=1)  # Get CPU usage as percentage
        return cpu_usage
    except Exception as e:
        log_message(error_log_path, f"Error retrieving CPU usage: {e}")
        return None

def log_fault(cpu_usage, timestamp):
    """Log the fault detection to the error.log file."""
    try:
        with open(error_log_path, 'a') as log_file:
            log_file.write(f"[{timestamp}] FAULT DETECTED - CPU Usage: {cpu_usage}%\n")
    except Exception as e:
        log_message(error_log_path, f"Error writing to error log file: {e}")

def predict_fault(cpu_usage):
    """Predict fault using the model based on current CPU usage."""
    try:
        # Ensure CPU usage is a valid number
        if cpu_usage is None:
            log_message(system_log_path, "Skipping prediction due to invalid CPU usage.")
            return
        
        # Make prediction (0 = No fault, 1 = Fault)
        prediction = model.predict([[cpu_usage]])  # Model expects a 2D array
        
        # Get the current timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
        
        # If fault predicted (1), log it
        if prediction == 1:
            log_fault(cpu_usage, timestamp)
            
            # Execute fault-handling subprocesses synchronously
            execute_subprocess("./sendMail.sh", str(timestamp), str(cpu_usage))
            execute_subprocess("./highCPUProcessKiller")
        else:
            log_message(system_log_path, f"[{timestamp}] No fault detected - CPU Usage: {cpu_usage}%")
    except Exception as e:
        log_message(error_log_path, f"Error during fault prediction: {e}")

def main():
    """Main function to automate fault prediction every minute."""
    log_message(system_log_path, "Starting fault prediction... Press Ctrl+C to stop.")
    
    while True:
        # Get the current CPU usage
        cpu_usage = get_cpu_usage()
        
        # Predict fault based on CPU usage
        predict_fault(cpu_usage)
        
        # Wait for 1 minute before checking again
        time.sleep(60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_message(system_log_path, "Fault prediction stopped by user (Ctrl+C).")
        exit(0)
    except Exception as e:
        log_message(error_log_path, f"Unexpected error: {e}")
        exit(1)
