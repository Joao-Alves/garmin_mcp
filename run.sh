#!/bin/bash

# Build the image
podman build -t garmin-mcp .

# Run the container
podman run -d \
  --name garmin-mcp \
  --restart unless-stopped \
  --read-only \
  --tmpfs /tmp \
  --env-file .env \
  -p 8000:8000 \
  garmin-mcp
