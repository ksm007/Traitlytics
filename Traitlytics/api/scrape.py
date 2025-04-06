

import os
import logging
import random
import time
import warnings
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from dotenv import load_dotenv

SESSION_ID = 'AQEDASfeZzgB6xg4AAABlNLoLqQAAAGWHhI-61YACANdqiMr2-2_ik2F0NNGAJAmcQGEhH_kZh2jy8_xG9vBSt0Njgx0EkKH7hhVY4jbToXsnOrVfP2L-lA9BoassbXtYdevo-OWfnowN9RWN7hvdG_l'

def scrape_website(url):
    driver = get_driver()
    try:
        login_to_linkedin(driver)  # Authenticate with LinkedIn
        logging.info(f"Scraping content from {url}")
        driver.get(url)
        time.sleep(3)  # Wait for the page to load
        profile_data = extract_profile_data(driver, url)
        return profile_data
    finally:
        driver.quit()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Suppress warnings
warnings.filterwarnings("ignore")

# Load environment variables
load_dotenv()

# Proxy list (Not used in this snippet, but kept for reference)
proxies = [
    "http://134.209.149.25:8099",  # Japan
    "http://133.167.65.66:80",     # United States
    "http://130.245.32.202:80",    # Japan
    "http://101.255.118.9:3127",   # Canada
    "http://133.18.234.13:80",     # United States
    "http://130.245.32.202:80",    # United States
    "http://132.148.167.243:2197", # Vietnam
    "http://101.101.217.36:80",    # United States
    "http://13.103.198.233:80"     # United States
]

# User-Agent list (Not directly used here, but available if needed)
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.62 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.111 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1"
]

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
def get_driver():
    options = webdriver.ChromeOptions()
    
    # Remove this line as it's causing issues
    # options.binary_location = "/usr/bin/chromium-browser"
    
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")

    # Use WebDriver Manager to automatically handle driver installation
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def use_session_cookie(driver, session_id):
    """Use a session ID to log in to LinkedIn."""
    logging.info("Using session ID to authenticate")
    driver.get('https://www.linkedin.com')  # Open LinkedIn home page
    driver.add_cookie({
        'name': 'li_at',
        'value': session_id,
        'domain': '.linkedin.com'
    })
    driver.refresh()

def login_to_linkedin(driver):
    driver.get("https://www.linkedin.com")
    logging.info("Logging in with session ID.")
    use_session_cookie(driver, SESSION_ID)
    driver.get("https://www.linkedin.com/feed/")  # Navigate to feed to confirm login

def extract_profile_data(driver, url):
    logging.info(f"Scraping profile data from {url}")
    driver.get(url)
    time.sleep(3)  # Wait for the page to load

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')

    profile_data = {}

    # Basic Profile Information
    name = soup.find('h1', {'class': 'text-heading-xlarge'})
    if name:
        profile_data['name'] = name.get_text(strip=True)

    # Headline
    headline = soup.find('div', {'class': 'text-body-medium break-words'})
    if headline:
        profile_data['headline'] = headline.get_text(strip=True)

    # About-us section
    about_section = soup.find('div', {'class': 'display-flex ph5 pv3'})
    if about_section:
        profile_data['about'] = about_section.get_text(strip=True)

    # Get all sections once and reuse
    sections = soup.find_all('section', {'class': 'artdeco-card pv-profile-card break-words mt2'})

     # Education Section Logic
    educations = None
    for sec in sections:
        if sec.find('div', {'id': 'education'}):
            educations = sec

    if educations:
        profile_data['education'] = educations.get_text(strip=True)
    else:
        profile_data['education'] = None

    # Experience section 
    experience_section = None
    sections = soup.find_all('section', {'class': 'artdeco-card pv-profile-card break-words mt2'})

    for sec in sections:
        if sec.find('div', {'id': 'experience'}):
            experience_section = sec
            break  # Stop after finding the first matching section

    profile_data['experience'] = []
    if experience_section:
        experience_items = experience_section.find_all('li')
        # Extract text from each experience item
        experience_texts = [item.get_text(strip=True) for item in experience_items]
        
        # Remove duplicates while preserving order
        profile_data['experience'] = list(dict.fromkeys(experience_texts))

    # Organizations Section Logic
    organizations_section = None
    for sec in sections:
        if sec.find('div', {'id': 'organizations'}):
            organizations_section = sec
            break

    profile_data['organizations'] = []
    if organizations_section:
        organization_items = organizations_section.find_all('li', {'class': 'artdeco-list__item'})
        for item in organization_items:
            org_name = item.find('span', {'aria-hidden': 'true'})
            org_role = item.find('span', {'class': 't-14 t-normal'})
            if org_name and org_role:
                org_data = {
                    'name': org_name.get_text(strip=True),
                    'role': org_role.get_text(strip=True)
                }
                profile_data['organizations'].append(org_data)
    
    return profile_data
