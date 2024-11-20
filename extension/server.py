# server.py

from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging

# Load environment variables from .env (if you have any other variables to load)
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

@app.route('/scrape', methods=['POST'])
def scrape_profile():
    data = request.json
    logging.debug(f"Received data: {data}")  # Log received data
    profile_url = data.get('url')
    if not profile_url:
        logging.debug("No URL provided in the request.")
        return jsonify({"error": "No URL provided"}), 400

    response = scrape_with_requests(profile_url)
    
    if response and response.status_code == 200:
        html_content = response.text
        logging.debug("Scraping successful. Extracting traits.")
        traits = extract_traits(html_content)  # Implement this function
        if traits:
            logging.debug(f"Extracted traits: {traits}")
            return jsonify({"traits": traits})
        else:
            logging.debug("No traits extracted from the HTML content.")
            return jsonify({"error": "No traits extracted from the profile"}), 400
    else:
        logging.debug(f"Scraping failed with status code: {response.status_code if response else 'No response'}")
        return jsonify({"error": "Failed to scrape the profile"}), 400

def scrape_with_requests(profile_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " 
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/95.0.4638.69 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.linkedin.com/",
    }
    
    try:
        response = requests.get(profile_url, headers=headers, timeout=30)
        logging.debug(f"Response Status Code: {response.status_code}")  # Debug
        if response.status_code != 200:
            # Log the first 500 characters to avoid huge logs
            logging.debug(f"Response Content (first 500 chars): {response.text[:500]}")
        else:
            logging.debug("Successfully fetched the profile page.")
        return response
    except requests.exceptions.RequestException as e:
        logging.debug(f"Exception during scraping: {e}")  # Debug
        return None

def extract_traits(html_content):
    """Extract traits from the HTML content."""
    soup = BeautifulSoup(html_content, "html.parser")
    traits = {}
    
    # Example: Extract the headline
    headline_tag = soup.find('h2', {'class': 'mt1 t-18 t-black t-normal'})
    if headline_tag:
        traits['headline'] = headline_tag.get_text(strip=True)
        logging.debug(f"Extracted headline: {traits['headline']}")
    else:
        logging.debug("Headline not found.")
    
    # Example: Extract skills (adjust selectors based on actual HTML structure)
    skills_section = soup.find('section', {'id': 'skills-section'})
    if skills_section:
        skills = [skill.get_text(strip=True) for skill in skills_section.find_all('span', 
                  {'class': 'pv-skill-category-entity__name-text'})]
        traits['skills'] = skills
        logging.debug(f"Extracted skills: {traits['skills']}")
    else:
        logging.debug("Skills section not found.")
    
    # Example: Extract experience
    experience_section = soup.find('section', {'id': 'experience-section'})
    if experience_section:
        experiences = []
        for position in experience_section.find_all('li', {'class': 'pv-entity__position-group-pager'}):
            company = position.find('span', {'class': 'pv-entity__secondary-title'})
            title = position.find('h3', {'class': 't-16 t-black t-bold'})
            dates = position.find('h4', {'class': 'pv-entity__date-range'})
            experience = {
                'company': company.get_text(strip=True) if company else None,
                'title': title.get_text(strip=True) if title else None,
                'dates': dates.get_text(strip=True) if dates else None,
            }
            experiences.append(experience)
        traits['experience'] = experiences
        logging.debug(f"Extracted experience: {traits['experience']}")
    else:
        logging.debug("Experience section not found.")
    
    # Add more extraction logic as needed
    
    if not traits:
        logging.debug("No traits extracted from the HTML content.")
    
    return traits

if __name__ == '__main__':
    app.run(port=5000, debug=True)
