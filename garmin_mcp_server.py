"""
Modular MCP Server for Garmin Connect Data
"""

import asyncio
import os
import datetime
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

from garth.exc import GarthHTTPError
from garminconnect import Garmin, GarminConnectAuthenticationError

# Import all modules
from modules import activity_management
from modules import health_wellness
from modules import user_profile
from modules import devices
from modules import gear_management
from modules import weight_management
from modules import challenges
from modules import training
from modules import workouts
from modules import data_management
from modules import womens_health

# Get credentials from environment
email = os.environ.get("GARMIN_EMAIL")
password = os.environ.get("GARMIN_PASSWORD")
tokenstore = os.getenv("GARMINTOKENS") or "~/.garminconnect"
tokenstore_base64 = os.getenv("GARMINTOKENS_BASE64") or "~/.garminconnect_base64"
mcp_mode = bool(os.getenv("MCP_MODE"))

def send_mcp_error(error_msg: str):
    """Send error message in MCP format"""
    if mcp_mode:
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": -32000,
                "message": error_msg
            },
            "id": None
        }
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()

def init_api(email, password):
    """Initialize Garmin API with your credentials."""
    if not email or not password:
        error_msg = "GARMIN_EMAIL and GARMIN_PASSWORD environment variables must be set"
        if mcp_mode:
            send_mcp_error(error_msg)
        else:
            print(error_msg)
        return None

    try:
        if mcp_mode:
            # Always use password auth in MCP mode for first-time setup
            garmin = Garmin(email=email, password=password, is_cn=False)
            garmin.login()
            # Ensure token directory exists
            token_dir = os.path.expanduser(tokenstore)
            os.makedirs(token_dir, exist_ok=True)
            garmin.garth.dump(tokenstore)
            return garmin
        else:
            # Try token-based login first in non-MCP mode
            garmin = Garmin()
            try:
                garmin.login(tokenstore)
                return garmin
            except (FileNotFoundError, GarthHTTPError):
                # Fall back to password auth
                garmin = Garmin(email=email, password=password, is_cn=False)
                garmin.login()
                token_dir = os.path.expanduser(tokenstore)
                os.makedirs(token_dir, exist_ok=True)
                garmin.garth.dump(tokenstore)
                # Save base64 tokens in non-MCP mode
                token_base64 = garmin.garth.dumps()
                dir_path = os.path.expanduser(tokenstore_base64)
                with open(dir_path, "w") as token_file:
                    token_file.write(token_base64)
                print(f"Oauth tokens stored for future use.\n")
                return garmin
    except (GarthHTTPError, GarminConnectAuthenticationError, requests.exceptions.HTTPError) as err:
        error_msg = f"Authentication error: {str(err)}"
        if mcp_mode:
            send_mcp_error(error_msg)
        else:
            print(error_msg)
        return None


def main():
    """Initialize the MCP server and register all tools"""
    
    # Initialize Garmin client
    garmin_client = init_api(email, password)
    if not garmin_client:
        if mcp_mode:
            send_mcp_error("Failed to initialize Garmin Connect client")
            sys.exit(1)  # Exit with error in MCP mode
        return
    
    if not mcp_mode:
        print("Garmin Connect client initialized successfully.")
    
    # Configure all modules with the Garmin client
    try:
        activity_management.configure(garmin_client)
        health_wellness.configure(garmin_client)
        user_profile.configure(garmin_client)
        devices.configure(garmin_client)
        gear_management.configure(garmin_client)
        weight_management.configure(garmin_client)
        challenges.configure(garmin_client)
        training.configure(garmin_client)
        workouts.configure(garmin_client)
        data_management.configure(garmin_client)
        womens_health.configure(garmin_client)
    except Exception as e:
        error_msg = f"Failed to configure modules: {str(e)}"
        if mcp_mode:
            send_mcp_error(error_msg)
            sys.exit(1)
        print(error_msg)
        return
    
    # Create the MCP app
    app = FastMCP("Garmin Connect v1.0")
    
    # Register tools from all modules
    try:
        app = activity_management.register_tools(app)
        app = health_wellness.register_tools(app)
        app = user_profile.register_tools(app)
        app = devices.register_tools(app)
        app = gear_management.register_tools(app)
        app = weight_management.register_tools(app)
        app = challenges.register_tools(app)
        app = training.register_tools(app)
        app = workouts.register_tools(app)
        app = data_management.register_tools(app)
        app = womens_health.register_tools(app)
    except Exception as e:
        error_msg = f"Failed to register tools: {str(e)}"
        if mcp_mode:
            send_mcp_error(error_msg)
            sys.exit(1)
        print(error_msg)
        return
    
    # Add activity listing tool directly to the app
    @app.tool()
    async def list_activities(limit: int = 5) -> str:
        """List recent Garmin activities"""
        try:
            activities = garmin_client.get_activities(0, limit)

            if not activities:
                return "No activities found."

            result = f"Last {len(activities)} activities:\n\n"
            for idx, activity in enumerate(activities, 1):
                result += f"--- Activity {idx} ---\n"
                result += f"Activity: {activity.get('activityName', 'Unknown')}\n"
                result += (
                    f"Type: {activity.get('activityType', {}).get('typeKey', 'Unknown')}\n"
                )
                result += f"Date: {activity.get('startTimeLocal', 'Unknown')}\n"
                result += f"ID: {activity.get('activityId', 'Unknown')}\n\n"

            return result
        except Exception as e:
            error_msg = f"Error retrieving activities: {str(e)}"
            if mcp_mode:
                send_mcp_error(error_msg)
            return error_msg
    
    # Run the MCP server
    app.run()


if __name__ == "__main__":
    main()
