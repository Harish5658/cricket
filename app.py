from flask import Flask, jsonify
import requests
import re
from bs4 import BeautifulSoup

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

            # Extract winning team info (e.g. "IND Won")
            winning_team_tag = match.find("div", class_="result")
            winning_team = winning_team_tag.find_next('span').text.strip() if winning_team_tag else "N/A"

            # Extract tournament or match reason
            tournament_tag = match.find("span", class_="reason")
            tournament = tournament_tag.text.strip() if tournament_tag else "N/A"

            # Match detail URL
            match_url = "https://crex.com" + match.find("a")["href"]

            # Fetch match description/details from match URL (try to get specific info)
            response_detail = requests.get(match_url)
            if response_detail.status_code == 200:
                soup_detail = BeautifulSoup(response_detail.content, 'lxml')

                # Try to extract a summary, e.g., from the first <div class="result"> span or similar
                result_div = soup_detail.find("div", class_="result")
                if result_div:
                    description_span = result_div.find('span')
                    match_description = description_span.text.strip() if description_span else "No description available"
                else:
                    match_description = "No description available"
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
            # Log error and continue without breaking API
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
    app.run(debug=True)

