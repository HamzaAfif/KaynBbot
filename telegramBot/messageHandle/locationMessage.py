from telegram import Update
from telegram.ext import CallbackContext




from dotenv import load_dotenv
import os
from messageHandle.textMessage import run_conversation
import json

import asyncio


async def handle_location(update: Update, context: CallbackContext):
    # Check if the update contains an edited message (for live location)
    if update.message and update.message.location:
        # Initial location
        message = update.message
    elif update.edited_message and update.edited_message.location:
        # Live location updates are sent as edited messages
        message = update.edited_message
    else:
        # Handle cases where there's no valid message or location
        print("Received an update without a valid message or location.")
        return

    user_id = message.from_user.id
    latitude = message.location.latitude
    longitude = message.location.longitude

    # Define the directory and filename
    directory = 'data/locations'
    filename = f'{directory}/user_{user_id}.json'
    
    # Create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)

    # Save location data to the JSON file
    location_data = {'user_id': user_id, 'latitude': latitude, 'longitude': longitude}
    with open(filename, 'w') as file:
        json.dump(location_data, file)

        
    system_message = f"The user has sent GPS coordinates: (Latitude: {latitude}, Longitude: {longitude})"
    
    assistant_reply = run_conversation(
        user_message="User has provided location data.",
        user_id=user_id,
        system_message=system_message
    )

    await update.message.reply_text(assistant_reply)
    # Start simulating live location updates asynchronously in the background, including `context`
    asyncio.create_task(simulate_live_location(user_id, latitude, longitude, context))

async def simulate_live_location(user_id, latitude, longitude, context):
    while True:
        # Simulate changes in location
        latitude += 0.0001
        longitude += 0.0001

        # Update the saved location in the JSON file
        directory = 'data/locations'
        filename = f'{directory}/user_{user_id}.json'
        if os.path.exists(filename):
            with open(filename, 'r+') as file:
                location_data = json.load(file)
                location_data['latitude'] = latitude
                location_data['longitude'] = longitude
                file.seek(0)
                json.dump(location_data, file)
                file.truncate()

        # Send the updated location (if desired) using the context to the user
        try:
            #await context.bot.send_location(
            #    chat_id=user_id,
            #    latitude=latitude,
            #    longitude=longitude
            #)
            pass
        except Exception as e:
            print(f"Failed to send location update: {e}")

        # Wait for a while before updating the location again
        await asyncio.sleep(5)

        # Optional: Commented out sending live location updates to the user
        # await context.bot.send_location(chat_id=user_id, latitude=latitude, longitude=longitude)