#!/bin/bash

# Start the Temporal server in the background
temporal server start-dev --ip 0.0.0.0 &

# Give the Temporal server some time to start up
sleep 5

# Run the Temporal operator command
temporal operator search-attribute create --name userId --type=Keyword

# Wait for the Temporal server process to complete
wait $!
