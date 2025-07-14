from flask import Flask, jsonify
import requests
import re
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

def scrape_matches():
    url = 'https://crex.com/series/1K7/champions-trophy-2025'
    response = requests.get(url)
    if response.status_code != 200:
        return {"error": "Failed to fetch main page"}

    soup = BeautifulSoup(response.content, 'lxml')
    matches = soup.find_all("div", class_="match-card-container")
    match_data = []

    for match in matches:
        try:
            # Extract team names (cleaned from numbers)
            first_team = match.find("div", class_="team-wrapper").text.split("/")[0]
            first_team = re.sub(r'\d+', '', first_team).strip()

            second_team = match.find("div", class_="team-wrapper right-team-name").text.split("/")[0]
            second_team = re.sub(r'\d+', '', second_team).strip()

            # Extract winning team info
            winning_team = match.find("div", class_="result").find_next('span').text.strip()

            # Extract tournament or match reason
            tournament = match.find("span", class_="reason").text.strip()

            # Match detail URL
            match_url = "https://crex.com" + match.find("a")["href"]

            # Fetch match description/details from match URL
            response_detail = requests.get(match_url)
            if response_detail.status_code == 200:
                soup_detail = BeautifulSoup(response_detail.content, 'lxml')
                match_description = ' '.join(soup_detail.text.split())
            else:
                match_description = "Details not available"

            match_info = {
                "first_team": first_team,
                "second_team": second_team,
                "winning_team": winning_team,
                "tournament": tournament,
                "match_url": match_url,
                "match_description": match_description
            }

            match_data.append(match_info)

        except Exception as e:
            # In case any part fails, skip that match to avoid breaking API
            print(f"Error processing a match: {e}")
            continue

    return match_data

@app.route("/live-matches", methods=["GET"])
def live_matches_api():
    data = scrape_matches()
    if isinstance(data, dict) and "error" in data:
        return jsonify(data), 500
    return jsonify(data)

if __name__ == "__main__":
    # Ensure Flask binds to the correct IP and port for the cloud environment
    port = int(os.environ.get("PORT", 5000))  # Use environment port or default to 5000
    app.run(host="0.0.0.0", port=port, debug=True)

