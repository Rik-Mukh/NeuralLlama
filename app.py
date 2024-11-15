from flask import Flask, redirect, request, session, url_for, render_template
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure Spotipy OAuth with necessary scopes
sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("REDIRECT_URI"),
    scope="playlist-read-private user-read-email"
)

# Step 1: Redirect to Spotify login
@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

# Step 2: Handle callback and obtain access token
@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    
    if token_info:
        session['access_token'] = token_info['access_token']
        return redirect(url_for('embed'))
    else:
        return "Authentication failed", 400

# Step 3: Display "NPC" playlist as an embedded Spotify player
@app.route('/embed')
def embed():
    if 'access_token' in session:
        # Initialize Spotify client with the access token
        sp = Spotify(auth=session['access_token'])
        
        # Fetch the user's playlists and find the playlist named "NPC"
        playlists = sp.current_user_playlists(limit=50)
        npc_playlist = None
        for playlist in playlists['items']:
            if playlist['name'].lower() == "npc":
                npc_playlist = playlist
                break

        # If the playlist is found, pass the playlist ID to the template to embed it
        if npc_playlist:
            playlist_id = npc_playlist['id']
            return render_template("playlist_embed.html", playlist_id=playlist_id)
        else:
            return "Playlist 'NPC' not found", 404
    else:
        return redirect(url_for('login'))

@app.route('/')
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(port=3000, debug=True)
