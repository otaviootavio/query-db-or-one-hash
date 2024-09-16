#!/bin/bash

# Function to clean up
cleanup() {
    echo "Cleaning up..."
    docker rm -f db-benchmark-container 2>/dev/null || true
    docker rmi db-benchmark 2>/dev/null || true
}

# Trap to catch interrupts and exits
trap cleanup EXIT

# Stop execution if any command fails
set -e

# Print commands before executing them
set -x

# Clean up any existing containers or images
cleanup

# Build the Docker image
docker build -t db-benchmark .

# Run the new container
docker run --name db-benchmark-container db-benchmark

# Print the logs of the container
docker logs db-benchmark-container

# If we get here, everything worked, so don't clean up
trap - EXIT