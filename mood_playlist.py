import webbrowser
from googleapiclient.discovery import build

API_KEY = "AIzaSyCjPs24D5SGfq_Nx54bwsvogGynKcDBR7Y"

MOOD_KEYWORDS = {
    "happy":     "happy upbeat songs playlist",
    "sad":       "sad emotional songs playlist",
    "angry":     "angry intense songs playlist",
    "romantic":  "romantic love songs playlist",
    "chill":     "chill relaxing songs playlist",
    "focused":   "focus study music playlist",
    "energetic": "energetic workout songs playlist",
    "sleepy":    "sleep calm music playlist",
    "motivated": "motivated inspirational songs playlist",
    "nostalgic": "nostalgic 90s songs playlist",
    "party":     "party songs playlist",
    "heartbreak":"heartbreak songs playlist",
}

MOOD_MESSAGES = {
    "happy":     "😊 You are amazing! Keep smiling and spread happiness around you!",
    "sad":       "💙 Hey it is okay to feel sad sometimes. Every storm runs out of rain. Brighter days are coming your way!",
    "angry":     "😤 Take a deep breath. You are stronger than your anger. Let the music calm your soul!",
    "romantic":  "❤️  Love is the most beautiful feeling in the world. Enjoy every moment of it!",
    "chill":     "😌 Relax and enjoy the moment. You deserve this peaceful time!",
    "focused":   "🎯 You are doing great! Stay focused and you will achieve everything you want!",
    "energetic": "⚡ You are unstoppable! Channel that energy and conquer the world today!",
    "sleepy":    "😴 Rest is important. Take care of yourself and sleep well tonight!",
    "motivated": "🚀 Believe in yourself! You are capable of achieving great things. Keep going!",
    "nostalgic": "🌟 Good old memories are always with you. Cherish them and smile!",
    "party":     "🎉 Life is a celebration! Enjoy every moment and dance like nobody is watching!",
    "heartbreak":"💔 It hurts now but you will come out stronger. You deserve all the love in the world!",
}

def search_playlists(mood):
    youtube = build("youtube", "v3", developerKey=API_KEY)
    request = youtube.search().list(part="snippet", q=MOOD_KEYWORDS[mood], type="playlist", maxResults=5)
    response = request.execute()
    return response.get("items", [])

def display_results(playlists):
    print("\n🎵 Top playlists found:\n")
    for i, item in enumerate(playlists, 1):
        title = item["snippet"]["title"]
        channel = item["snippet"]["channelTitle"]
        playlist_id = item["id"]["playlistId"]
        url = f"https://www.youtube.com/playlist?list={playlist_id}"
        print(f"{i}. {title}")
        print(f"   Channel: {channel}")
        print(f"   Link: {url}\n")
    return playlists

def open_playlist(playlists):
    choice = input("Enter playlist number to open (or 0 to skip): ").strip()
    if choice.isdigit():
        index = int(choice)
        if 1 <= index <= len(playlists):
            playlist_id = playlists[index - 1]["id"]["playlistId"]
            url = f"https://www.youtube.com/playlist?list={playlist_id}"
            print(f"\n🚀 Opening playlist in browser...")
            webbrowser.open(url)

def main():
    print("=" * 40)
    print("   🎧 Mood-Based Playlist Finder")
    print("=" * 40)
    print("\nAvailable moods:")
    for mood in MOOD_KEYWORDS:
        print(f"  - {mood}")
    mood = input("\nEnter your mood: ").strip().lower()
    if mood not in MOOD_KEYWORDS:
        print(f"\n❌ '{mood}' is not a recognized mood.")
        print("Please choose from:", ", ".join(MOOD_KEYWORDS.keys()))
        return

    # ✅ Show positive message
    print(f"\n{MOOD_MESSAGES[mood]}")
    print("\n🎵 Don't worry, listen to these songs...\n")

    print(f"\n🔍 Searching playlists for mood: {mood}...")
    playlists = search_playlists(mood)
    if not playlists:
        print("No playlists found. Try again.")
        return
    display_results(playlists)
    open_playlist(playlists)

if __name__ == "__main__":
    main()