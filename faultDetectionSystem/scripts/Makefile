# Makefile for compiling the CPU high usage process killer

# Compiler
CC = gcc

# Compiler flags
CFLAGS = -Wall -Wextra -O2

# Output executable name
OUTPUT = highCPUProcessKiller

# Source file
SRC = highCPUProcess.c

# Object file
OBJ = $(SRC:.c=.o)

# Default target
all: $(OUTPUT)

# Rule to build the executable
$(OUTPUT): $(OBJ)
	$(CC) $(OBJ) -o $(OUTPUT)

# Rule to build object file from source
$(OBJ): $(SRC)
	$(CC) $(CFLAGS) -c $(SRC)

# Clean rule
clean:
	rm -f $(OBJ) $(OUTPUT)

.PHONY: all clean

