from flask import Flask, render_template, request
from googleapiclient.discovery import build
import os
import random

app = Flask(__name__)

API_KEY = "AIzaSyCjPs24D5SGfq_Nx54bwsvogGynKcDBR7Y"

MOOD_KEYWORDS = {
    "happy":      "happy upbeat songs playlist",
    "sad":        "sad emotional songs playlist",
    "angry":      "angry intense songs playlist",
    "romantic":   "romantic love songs playlist",
    "chill":      "chill relaxing songs playlist",
    "focused":    "focus study music playlist",
    "energetic":  "energetic workout songs playlist",
    "sleepy":     "sleep calm music playlist",
    "motivated":  "motivated inspirational songs playlist",
    "nostalgic":  "nostalgic 90s songs playlist",
    "party":      "party songs playlist",
    "heartbreak": "heartbreak songs playlist"  
}

MOOD_MESSAGES = {
    "happy":      "😊 You are amazing! Keep smiling and spread happiness around you!",
    "sad":        "💙 Hey it is okay to feel sad. Brighter days are coming your way!",
    "angry":      "😤 Take a deep breath. Let the music calm your soul!",
    "romantic":   "❤️ Love is the most beautiful feeling. Enjoy every moment!",
    "chill":      "😌 Relax and enjoy the moment. You deserve this peaceful time!",
    "focused":    "🎯 You are doing great! Stay focused and achieve everything!",
    "energetic":  "⚡ You are unstoppable! Conquer the world today!",
    "sleepy":     "😴 Rest is important. Take care of yourself!",
    "motivated":  "🚀 Believe in yourself! You are capable of great things!",
    "nostalgic":  "🌟 Good old memories are always with you. Cherish them!",
    "party":      "🎉 Life is a celebration! Dance like nobody is watching!",
    "heartbreak": "💔 You will come out stronger. You deserve all the love!",
}

MOOD_EMOJIS = {
    "happy":      "😊",
    "sad":        "😢",
    "angry":      "😤",
    "romantic":   "❤️",
    "chill":      "😌",
    "focused":    "🎯",
    "energetic":  "⚡",
    "sleepy":     "😴",
    "motivated":  "🚀",
    "nostalgic":  "🌟",
    "party":      "🎉",
    "heartbreak": "💔",
}

def search_playlists(mood):
    youtube = build("youtube", "v3", developerKey=API_KEY)
    request = youtube.search().list(
        part="snippet",
        q=MOOD_KEYWORDS[mood],
        type="playlist",
        maxResults=5
    )
    response = request.execute()
    return response.get("items", [])

@app.route("/", methods=["GET", "POST"])
def index():
    playlists = []
    mood = None
    message = None
    error = None
    if request.method == "POST":
        mood = request.form.get("mood").strip().lower()
        if mood not in MOOD_KEYWORDS:
            error = f"'{mood}' is not a recognized mood!"
        else:
            message = MOOD_MESSAGES[mood]
            playlists = search_playlists(mood)
    return render_template("index.html",
                           playlists=playlists,
                           mood=mood,
                           message=message,
                           error=error,
                           mood_keywords=MOOD_KEYWORDS,
                           mood_emojis=MOOD_EMOJIS)
    @app.route("/surprise")
def surprise():
    mood = random.choice(list(MOOD_KEYWORDS.keys()))
    message = MOOD_MESSAGES[mood]
    playlists = search_playlists(mood)
    return render_template("index.html",
                           playlists=playlists,
                           mood=mood,
                           message=message,
                           error=None,
                           mood_keywords=MOOD_KEYWORDS,
                           mood_emojis=MOOD_EMOJIS)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

