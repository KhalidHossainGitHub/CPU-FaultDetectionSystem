#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_BUFFER_SIZE 2048
#define MIN_CPU_USAGE 5.0

// Function to fetch and filter processes using `top`
void fetch_and_filter_processes() {
    FILE *fp;
    char line[MAX_BUFFER_SIZE];
    char command[MAX_BUFFER_SIZE];
    int pid;
    float cpu_usage;
    int result;

    // Inform the user about quitting the program
    printf("Press 'q' to quit at any time.\n\n");

    // Command to capture the output of top, filtering for tasks using > 5% CPU
    const char *top_command =
        "top -b -n 1 | awk 'NR>7 {if ($9 > 5) print $1, $9, $12}'";

    fp = popen(top_command, "r");
    if (fp == NULL) {
        fprintf(stderr, "Error: Failed to execute top command.\n");
        exit(1);
    }

    int process_found = 0; // Flag to track if processes were found
    int at_least_one_displayed = 0; // Track if we've already displayed a process

    // Read the output of the top command
    while (fgets(line, sizeof(line), fp) != NULL) {
        // Parse PID, CPU usage, and command name
        result = sscanf(line, "%d %f %[^\n]", &pid, &cpu_usage, command);
        if (result != 3) {
            // Skip lines that don't match the format
            continue;
        }

        process_found = 1; // At least one process is found

        // Display process information
        printf("PID: %d - Command: %s - CPU usage: %.2f%%\n", pid, command, cpu_usage);
        printf("Would you like to kill this process? (y/n, or q to quit): ");

        // Get user input
        char choice;
        scanf(" %c", &choice);

        if (choice == 'q' || choice == 'Q') {
            printf("Exiting the program.\n");
            break;
        } else if (choice == 'y' || choice == 'Y') {
            // Kill the process
            char kill_command[MAX_BUFFER_SIZE];
            snprintf(kill_command, sizeof(kill_command), "kill -9 %d", pid);
            int kill_result = system(kill_command);
            if (kill_result == 0) {
                printf("Process %d terminated successfully.\n", pid);
            } else {
                fprintf(stderr, "Error: Failed to terminate process %d.\n", pid);
            }
            break; // Exit after killing a process
        } else if (choice == 'n' || choice == 'N') {
            // Check if this was the last process
            if (fgets(line, sizeof(line), fp) == NULL) {
                // No more processes, exit the loop
                printf("No more processes to review. Exiting program.\n");
                break;
            }
            // Reset the file pointer to reprocess the current line in the next iteration
            ungetc('\n', fp);
            printf("Skipping to the next process...\n");
        } else {
            printf("Invalid input. Please enter 'y', 'n', or 'q'.\n");
        }
    }

    pclose(fp);

    if (!process_found) {
        printf("No processes with CPU usage > %.1f%% found.\n", MIN_CPU_USAGE);
    }
}

int main() {
    // Display introductory message
    printf("This program lists all non-root processes with CPU usage > %.1f%% sorted by CPU usage.\n", MIN_CPU_USAGE);
    printf("You can choose to kill a process or quit by typing 'q'.\n\n");

    // Retrieve and handle processes
    fetch_and_filter_processes();

    return 0;
}

