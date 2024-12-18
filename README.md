# CPU Fault Detection System Using Machine Learning

The **CPU Fault Detection System** is a proactive fault detection tool designed to monitor CPU performance in real-time, identify potential faults, and enhance system reliability through automation and machine learning techniques. This project integrates core systems programming, machine learning, and automated alert mechanisms to deliver a robust solution for fault management in Linux environments.

<p align="center">
  <img width="932" alt="image" src="https://github.com/user-attachments/assets/cpu_fault_detection_system.png">
</p>

## Project Overview

The CPU Fault Detection System enables:

- **Real-time Monitoring**: Continuous tracking of CPU usage and performance.
- **Fault Prediction**: Uses a machine learning model trained with logistic regression to identify faults.
- **Automated Alerts**: Logs faults and notifies users via email with details and recommended actions.
- **Fault Resolution Assistance**: Identifies CPU-heavy processes and provides options to terminate them.

## Features

- **Automated Data Pipeline**:
  - Collects real-time CPU performance data.
  - Processes raw data into a structured format for model training.
  - Trains a machine learning model to predict CPU faults.
- **Fault Detection**: Continuously monitors CPU usage and identifies anomalies.
- **Visualization**: Generates graphs to visualize model performance.
- **Alert Mechanism**: Logs faults and sends email notifications to designated users.
- **Process Management**: Offers options to terminate high-CPU processes for system optimization.

## Technologies Used

- **Bash**: For scripting data collection and automation.
- **Perl**: For data preprocessing.
- **Python**: For machine learning model training and fault prediction.
- **Logistic Regression**: For accurate fault predictions.
- **Linux Tools**: Includes `make`, `msmtp`, and `tmux` for system integration and error handling.

## Prerequisites

- **Operating System**: Ubuntu Linux distribution.
- **Software**:
  - `make`
  - `msmtp` and `msmtp-mta` for email alerts
  - `python3` and `pip`
  - Python packages: `virtualenv`, `numpy`, `pandas`, `scikit-learn`, `psutil`, `matplotlib`

## Setup and Installation

1. **Install Required Software**:
   ```bash
   sudo apt update
   sudo apt-get install make tmux msmtp msmtp-mta python3 python-pip
   ```

2. **Create Directory Structure**:
   ```bash
   mkdir -p faultDetectionSystem/{logs,scripts,data}
   cd faultDetectionSystem/logs
   touch system.log error.log
   ```

3. **Write Scripts**:
   - Write necessary scripts in the `scripts` directory.
   - Ensure scripts have read, write, and execute permissions.

4. **Setup Virtual Environment**:
   ```bash
   cd faultDetectionSystem
   pip install virtualenv
   virtualenv faultDetection
   source faultDetection/bin/activate
   pip install numpy pandas scikit-learn psutil matplotlib
   ```

5. **Configure Email Alerts**:
   - Create `.msmtprc`:
     ```bash
     nano ~/.msmtprc
     ```
     Example configuration:
     ```plaintext
     account gmail
     host smtp.gmail.com
     port 587
     from your_email@gmail.com
     auth on
     user your_email@gmail.com
     password your_app_password
     tls on
     tls_starttls on
     logfile ~/.msmtp.log
     account default : gmail
     ```
   - Set appropriate file permissions:
     ```bash
     chmod 600 ~/.msmtprc
     ```

## How to Run the System

1. **Start Data Collection**:
   ```bash
   source faultDetection/bin/activate
   cd scripts
   ./dataCollection.sh [duration_in_minutes] &
   ```

2. **Monitor Logs and Data**:
   - View logs: `cat logs/system.log` or `cat logs/error.log`
   - View data: `cat data/rawData.txt` or `cat data/processedData.csv`
   - View graph: `xdg-open data/resourceUsageGraph.png`

3. **Run Fault Detection**:
   ```bash
   python faultPrediction.py &
   ```

4. **Handle High CPU Usage**:
   - Use the `highCPUProcessKiller` script to manage resource-heavy processes.

## Input/Output

- **Input**: Real-time CPU usage data and duration of data collection.
- **Output**:
  - Logs (system and error logs).
  - Processed data (CSV file).
  - Trained machine learning model (pickle file).
  - Graph of resource usage.
  - Email notifications for faults.

## Testing

- Test each script individually to ensure proper error handling and output generation.
- Verify fault detection and alert mechanisms using controlled CPU usage scenarios.
- Confirm email notifications are sent successfully with accurate fault details.

---

This project showcases the integration of machine learning and automation for proactive system management and optimization. For further details, refer to the project's documentation or contact the development team.
