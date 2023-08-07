import discord
from discord import Intents
import requests
import asyncio
import os
from datetime import datetime

API_URL = "https://traffic.mdpd.com/api/traffic"
PROBE_INTERVAL = 15  # Adjusted for testing purposes

latest_timestamp = datetime.min  # Initialize to the smallest possible datetime

intents = Intents.default()
intents.messages = True
intents.guilds = True

client = discord.Client(intents=intents)
channel_preferences = {}

# Obtain working directory
script_path = os.path.abspath(__file__)
script_directory = os.path.dirname(script_path)
print("Script directory:", script_directory)

configFileTxt = (script_directory+"/config.txt")
serverChannelConfig = (script_directory+"/servers_channels_config.txt")


def load_config():
    config = {}
    with open(configFileTxt, "r") as file:
        for line in file:
            key, value = line.strip().split(" = ")
            config[key] = value
    return config

#obtain token
config = load_config()
TOKEN = config['token']

# Load server preferences from the file
def load_preferences():
    if os.path.exists(serverChannelConfig):
        print(serverChannelConfig)
        print("Found servers_channels_config.txt file. Loading preferences...")
        with open(serverChannelConfig, "r") as file:
            for line in file:
                server_id, channel_id = line.strip().split(":")
                channel_preferences[int(server_id)] = int(channel_id)
        print("Loaded preferences:", channel_preferences)
    else:
        print("No server_channels_config.txt file found.")

# Save server preferences to the file
def save_preferences():
    print("Saving preferences to servers_channels_config.txt...")
    with open(serverChannelConfig, "w") as file:
        for server_id, channel_id in channel_preferences.items():
            file.write(f"{server_id}:{channel_id}\n")
    print("Preferences saved.")

def fetch_traffic_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching traffic data:", response.status_code)
        return None

def print_traffic_data(data):
    for entry in data:
        message = f"CreateTime: {entry['CreateTime']}\n" \
                  f"Signal: {entry['Signal']}\n" \
                  f"Address: {entry['Address']}\n" \
                  f"Location: {entry['Location']}\n\n"
        yield message

@client.event
async def on_ready():
    print(f"Bot logged in as {client.user.name} ({client.user.id})")
    load_preferences()

@client.event
async def on_message(message):
    # If the message is from the bot itself, ignore
    if message.author == client.user:
        return

    # Log the message for observation
    content = message.content.strip().lower()
    print(f"Received message from {message.author.name}: {content}")
    
    # Check if the content ends with '!setup'
    if content.endswith('!setup'):
        print("[DEBUG] Detected !setup command. Proceeding to process...")
        
        # Update the channel preferences and save them
        channel_preferences[message.guild.id] = message.channel.id
        print("[DEBUG] Updated channel preferences in memory.")
        
        save_preferences()
        print("[DEBUG] Preferences saved to file.")
                
        # Send a confirmation message
        await message.channel.send(f"Setup complete! I'll send traffic updates to this channel: {message.channel.mention}.")
        print(f"[DEBUG] Setup completed for server: {message.guild.name}, channel: {message.channel.name}")
        return
    else:
        print("[DEBUG] The received message did not match the !setup command.")
    
latest_timestamp = datetime.min  # Initialize to the smallest possible datetime

async def broadcast_traffic_data():
    global latest_timestamp

    while True:
        for guild_id, channel_id in channel_preferences.items():
            channel = client.get_channel(channel_id)
            if channel:
                traffic_data = fetch_traffic_data()

                # Filter for new alerts based on timestamp
                new_alerts = [alert for alert in traffic_data if datetime.fromisoformat(alert['CreateTime']) > latest_timestamp]

                if new_alerts:
                    print(f"Sending traffic data to channel: {channel.name} ({channel.id})")

                    # Update the latest timestamp
                    latest_timestamp = max(datetime.fromisoformat(alert['CreateTime']) for alert in new_alerts)

                    for message in print_traffic_data(new_alerts):
                        await channel.send(message)
                        print(f"Sent message: {message}")
                    
                    print("Traffic data sent successfully")
                else:
                    print("No new traffic data to send.")
        print(f"Next probe in {PROBE_INTERVAL} seconds...")
        await asyncio.sleep(PROBE_INTERVAL)

async def main():
    bot_task = asyncio.create_task(client.start(TOKEN))
    broadcast_task = asyncio.create_task(broadcast_traffic_data())
    await bot_task

asyncio.run(main())
