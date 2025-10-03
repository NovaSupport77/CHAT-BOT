#!/bin/bash

# 1. Run the Pyrogram Bot in the background (&)
# The '&' is crucial! It tells the shell to run the bot and immediately move to the next command.
echo "✅ Starting Advanced Chatbot in background..."
python3 advanced_chatbot_final.py &

# 2. Start a simple HTTP server
# This command listens on port 8080 (Render's requirement) and keeps the Web Service running.
echo "✅ Starting dummy HTTP server on port 8080 to satisfy Render..."
python3 -m http.server 8080
