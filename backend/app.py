from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import os

import ipl
import jugaad

# Create Flask app FIRST
app = Flask(__name__)

# Enable CORS for all origins (needed for GitHub Pages)
CORS(app)

@app.route('/')
def home():
    return "IPL API is Online"

# ---------------- TEAMS ----------------
@app.route('/api/teams')
def teams():
    return jsonify(ipl.teamsAPI())

# ---------------- TEAM VS TEAM ----------------
@app.route('/api/teamvteam')
def teamvteam():
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')

    if not team1 or not team2:
        return jsonify({'error': 'team1 and team2 parameters are required'}), 400

    return jsonify(ipl.teamVteamAPI(team1, team2))

# ---------------- TEAM RECORD ----------------
@app.route('/api/team-record')
def team_record():
    team_name = request.args.get('team')

    if not team_name:
        return jsonify({'error': 'team parameter is required'}), 400

    response = jugaad.teamAPI(team_name)
    return Response(response, mimetype='application/json')

# ---------------- BATTING RECORD ----------------
@app.route('/api/batting-record')
def batting_record():
    batsman_name = request.args.get('batsman')

    if not batsman_name:
        return jsonify({'error': 'batsman parameter is required'}), 400

    response = jugaad.batsmanAPI(batsman_name)
    return Response(response, mimetype='application/json')

# ---------------- BOWLING RECORD ----------------
@app.route('/api/bowling-record')
def bowling_record():
    bowler_name = request.args.get('bowler')

    if not bowler_name:
        return jsonify({'error': 'bowler parameter is required'}), 400

    response = jugaad.bowlerAPI(bowler_name)
    return Response(response, mimetype='application/json')

# ---------------- RUN (Render compatible) ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

