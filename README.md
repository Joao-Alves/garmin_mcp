# Garmin MCP Server

This Model Context Protocol (MCP) server connects to Garmin Connect and exposes your fitness and health data to Claude and other MCP-compatible clients.

## Features

- List recent activities
- Get detailed activity information
- Access health metrics (steps, heart rate, sleep)
- View body composition data
- Track training status and readiness
- Monitor devices and gear
- Manage workouts and challenges
- Track women's health data
- Monitor hydration and nutrition

## Setup

1. Install the required packages in a new environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

2. Create a `.env` file in the project root with your Garmin credentials:

```
GARMIN_EMAIL=your.email@example.com
GARMIN_PASSWORD=your-password
```

## Running as an MCP Server

The server implements the Model Context Protocol (MCP), allowing AI assistants to access your Garmin data. There are several ways to run it:

### 1. Direct Python Execution

```bash
python garmin_mcp_server.py
```

### 2. With Claude Desktop

1. Create/edit your Claude Desktop configuration:

Location:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

Add this configuration:

```json
{
  "mcpServers": {
    "garmin": {
      "command": "<path_to_venv>/python",
      "args": ["<path_to>/garmin_mcp_server.py"]
    }
  }
}
```

2. Restart Claude Desktop

### 3. Container Deployment

Using Podman:

```bash
# Using the provided script
./run.sh

# Or manually
podman build -t garmin-mcp .
podman run -d \
  --name garmin-mcp \
  --restart unless-stopped \
  --read-only \
  --tmpfs /tmp \
  --env-file .env \
  -p 8000:8000 \
  garmin-mcp
```

To use the container with MCP:

1. Create/edit your MCP client configuration:

Location:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

Add this configuration for stdio-based communication (recommended):

```json
{
  "mcpServers": {
    "garmin": {
      "command": "podman",
      "args": ["run", "--rm", "-i", "-v", "${HOME}/.garminconnect:/app/.garminconnect:Z", "-e", "MCP_MODE=1", "-e", "GARMIN_EMAIL=${GARMIN_EMAIL}", "-e", "GARMIN_PASSWORD=${GARMIN_PASSWORD}", "garmin-mcp"]
    }
  }
}
```

The configuration supports environment variables:
- `${HOME}/.garminconnect` - Path to store OAuth tokens
- `${GARMIN_EMAIL}` - Your Garmin Connect email
- `${GARMIN_PASSWORD}` - Your Garmin Connect password

Make sure to set these environment variables in your shell or your Claude Desktop environment:
```bash
export GARMIN_EMAIL="your.email@example.com"
export GARMIN_PASSWORD="your_password"
```

2. Make sure the container image is built:
```bash
podman images | grep garmin-mcp
```

3. Check the container logs if needed:
```bash
podman logs garmin-mcp
```

### 4. Development Testing

Use the MCP Inspector for direct testing:

```bash
npx @modelcontextprotocol/inspector python garmin_mcp_server.py
```

## Available MCP Tools

The server provides tools for:

- Activity Management
  - List activities
  - Get activity details
  - Access splits and segments
  
- Health & Wellness
  - Steps data
  - Heart rate monitoring
  - Sleep tracking
  - Stress levels
  - Body Battery™
  - Blood pressure
  - SpO2 measurements
  
- Training & Performance
  - Training status
  - Training readiness
  - VO2 Max
  - Training effect
  - Running dynamics
  
- Device Management
  - List devices
  - Device settings
  - Solar charging data
  - Device alarms

## Security Considerations

1. Credential Security:
   - Store credentials in `.env` file (never commit to repository)
   - Token storage is encrypted and secure
   - Container runs as non-root user

2. Data Privacy:
   - All data remains local
   - No third-party data sharing
   - Secure token management

3. Container Security:
   - Read-only filesystem
   - Non-root user
   - Minimal base image
   - Health monitoring

## Troubleshooting

1. Authentication Issues:
   - Verify credentials in `.env` file
   - Check Garmin Connect account status
   - Clear and regenerate tokens if needed
   - Try logging in to Garmin Connect website first

2. Connection Problems:
   - Check internet connectivity
   - Verify Garmin Connect API status
   - Check firewall settings
   - Review container logs

3. MCP Integration:
   - Verify MCP client configuration
   - Check server logs
   - Test with MCP Inspector
   - Verify port accessibility

Logs Location:
- Container: `podman logs garmin-mcp`
- Claude Desktop:
  - macOS: `~/Library/Logs/Claude/mcp-server-garmin.log`
  - Windows: `%APPDATA%\Claude\logs\mcp-server-garmin.log`
  - Linux: `~/.local/share/Claude/logs/mcp-server-garmin.log`