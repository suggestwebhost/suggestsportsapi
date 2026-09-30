import os
from flask import Flask, jsonify
import requests

app = Flask(__name__)

# 1. It looks for a private environment variable named 'SPORTS_DB_KEY'.
# 2. If it doesn't find one, it automatically falls back to the free '123' test key.
API_KEY = os.environ.get("SPORTS_DB_KEY")
THE_SPORTS_DB_BASE_URL = f"https://thesportsdb.com/{API_KEY}"

@app.route('/team-sprites/<team_name>', methods=['GET'])
def get_team_sprites(team_name):
    search_url = f"{THE_SPORTS_DB_BASE_URL}/searchteams.php?t={team_name}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        search_response = requests.get(search_url, headers=headers)
        search_response.raise_for_status()
        search_data = search_response.json()
        
        if not search_data or not search_data.get('teams'):
            return jsonify({"error": f"No assets found for '{team_name}'"}), 404
            
        team_info = search_data['teams'][0] # Grab the first team match
        
        return jsonify({
            "team_name": team_info.get("strTeam"),
            "badge_url": team_info.get("strBadge"),          
            "jersey_url": team_info.get("strEquipment"),      
            "logo_url": team_info.get("strLogo"),            
            "banner_url": team_info.get("strBanner")          
        }), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to connect to provider backend", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
