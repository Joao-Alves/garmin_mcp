# Use Python slim image for smaller attack surface
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -r garmin

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MCP_MODE=1 \
    GARMINTOKENS="/app/.garminconnect"

# Create token directory with proper permissions
RUN mkdir -p /app/.garminconnect && \
    chown -R garmin:garmin /app/.garminconnect

# Copy application code
COPY . .

# Set proper permissions
RUN chown -R garmin:garmin /app

# Switch to non-root user
USER garmin

# Run the application
CMD ["python", "garmin_mcp_server.py"]