from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# JioSaavn API base URL (Unofficial)
JIOSAAVN_API = "https://saavn.dev"
def get_song_data(song_query):
    """fetch song details from JioSaavn API"""
    params = {
        '_format': 'json',
        'query': song_query,
        'cc': 'in',
        '_marker': '0',
        'ctx': 'web6dot0'
    }
    search_url = JIOSAAVN_API+"/api/search/songs"

    response = requests.get(search_url, params=params, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code == 200:
        return response.json()
    return None

def get_song_data_by_id(id):
    """fetch song details from JioSaavn API"""
    params = {
        '_format': 'json',
        'id': id,
        'cc': 'in',
        'ctx': 'web6dot0'
        }
    search_url = JIOSAAVN_API+f"/api/songs/{id}"
    response = requests.get(search_url, params=params, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code == 200:
        return response.json()
    return None

@app.route('/')
def home():
    return jsonify({"message": "Air music API is running!"})
    
@app.route('/songs', methods=['GET'])
def search_song():
    """Search for a song with filtered song data"""
    song_query = request.args.get('query')
    
    if not song_query:
        return jsonify({"error": "Song name required!"}), 400

    data = get_song_data(song_query)
    if data and "data" in data and "results" in data["data"]:
        filtered_results = []
        
        for song in data["data"]["results"]:
            filtered_results.append({
                "id": song.get("id"),
                "name": song.get("name"),
                "language": song.get("language"),
                "url": song.get("url"),
                "image": song.get("image", [{}])[-1].get("url"),  # get last/highest quality image
                # "downloadUrl": song.get("downloadUrl", [])
                "musicUrl": song.get("downloadUrl", [{}])[-1].get("url")
            })
        return jsonify(filtered_results)
    return jsonify({"error": "No data found!"}), 404

@app.route('/song/<id>', methods=['GET'])
def get_song(id):
    """Return song by id with filtered song data for the given ID"""
    response = get_song_data_by_id(id)
    if response and response.get("success") and isinstance(response.get("data"), list):
        for song in response["data"]:
            if song.get("id") == id:
                # Filter only required fields
                filtered_data = {
                    "id": song.get("id"),
                    "name": song.get("name"),
                    "language": song.get("language"),
                    "hasLyrics": song.get("hasLyrics"),
                    "image": song.get("image", []),
                    "downloadUrl": song.get("downloadUrl", []),
                    "releaseDate": song.get("releaseDate"),
                    "playCount": song.get("playCount")
                    # "artists": song.get("artists", {}).get("primary", [])
                }
                return jsonify(filtered_data)
        return jsonify({"error": "Song not found with given ID"}), 404
    return jsonify({"error": "Invalid response from API"}), 500

if __name__ == "__main__":
    app.run(debug=False,threaded=True)
