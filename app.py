import os
from flask import Flask, jsonify, render_template_string
import requests

app = Flask(__name__)

# Fallback developer token '3'
API_KEY = os.environ.get("SPORTS_DB_KEY")
THE_SPORTS_DB_BASE_URL = f"https://thesportsdb.com{API_KEY}"

def fetch_team_data(team_name):
    search_url = f"{THE_SPORTS_DB_BASE_URL}/searchteams.php?t={team_name}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Check if 'teams' exists and is a valid non-empty list
        if data and isinstance(data.get('teams'), list) and len(data['teams']) > 0:
            return data['teams'][0]  # SAFE FIX: Grab the first element dictionary
    except Exception as e:
        print(f"Fetch log error: {str(e)}") # Prints the error in your terminal console
    return None

# Route 1: Raw JSON endpoint
@app.route('/team-sprites/<team_name>', methods=['GET'])
def get_team_sprites(team_name):
    team_info = fetch_team_data(team_name)
    if not team_info:
        return jsonify({"error": f"No assets found for '{team_name}'"}), 404
        
    return jsonify({
        "team_name": team_info.get("strTeam"),
        "badge_url": team_info.get("strBadge"),          
        "jersey_url": team_info.get("strEquipment"),      
        "logo_url": team_info.get("strLogo"),            
        "banner_url": team_info.get("strBanner")          
    }), 200

# Route 2: HTML Image Viewer
@app.route('/view-sprites/<team_name>', methods=['GET'])
def view_team_sprites(team_name):
    team_info = fetch_team_data(team_name)
    if not team_info:
        return f"<h1>Team '{team_name}' not found or has no available data.</h1>", 404

    placeholder = "https://placehold.co"
    
    badge = team_info.get("strBadge") or placeholder
    jersey = team_info.get("strEquipment") or placeholder
    logo = team_info.get("strLogo") or placeholder
    banner = team_info.get("strBanner") or placeholder
    name = team_info.get("strTeam", team_name)

    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{name} Sprite Viewer</title>
        <style>
            body {{ font-family: sans-serif; background: #f4f6f9; text-align: center; padding: 20px; color: #333; }}
            .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            h1 {{ color: #111; margin-bottom: 30px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 20px; }}
            .card {{ background: #fafafa; border: 1px solid #eee; padding: 15px; border-radius: 8px; text-align: center; }}
            .card img {{ max-width: 100%; height: auto; max-height: 150px; object-fit: contain; border-radius: 4px; }}
            .card h3 {{ font-size: 16px; margin: 10px 0 5px 0; color: #555; }}
            .banner-box {{ margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px; }}
            .banner-box img {{ max-width: 100%; height: auto; max-height: 100px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎨 {name} Sprite Viewer</h1>
            <div class="grid">
                <div class="card">
                    <h3>Official Badge</h3>
                    <img src="{badge}" alt="Badge">
                </div>
                <div class="card">
                    <h3>Team Jersey</h3>
                    <img src="{jersey}" alt="Jersey">
                </div>
                <div class="card">
                    <h3>Brand Logo</h3>
                    <img src="{logo}" alt="Logo">
                </div>
            </div>
            <div class="banner-box">
                <h3>Horizontal Banner</h3>
                <img src="{banner}" alt="Banner">
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
