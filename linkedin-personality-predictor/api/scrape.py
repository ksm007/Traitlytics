

import os
import logging
import random
import time
import warnings
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from dotenv import load_dotenv

SESSION_ID = 'AQEDATD5GXwE5GoFAAABk4pptCIAAAGT1lWhQU0AJIkW8uW6U2Pl4NfzgKEXPvtDBZsFqd28655XQfqvVXYR4qM4moHGWNzPZIqxVmsW6hRRUa623DdQqEmUN37ahRwa-bCDrLrGhwndEpdWpVvJyZHw'

def scrape_website(url):
    """Scrape the website and return the raw HTML content."""
    driver = get_driver()
    try:
        login_to_linkedin(driver)  # Use session ID to authenticate
        logging.info(f"Scraping content from {url}")
        driver.get(url)
        time.sleep(3)  # Wait for the page to load
        raw_html = driver.page_source  # Get the page source
        return raw_html
    finally:
        driver.quit()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Suppress warnings
warnings.filterwarnings("ignore")

# Load environment variables
load_dotenv()

# Proxy list
proxies = [
    "http://134.209.149.25:8099",  # Japan
    "http://133.167.65.66:80",   # United States
    "http://130.245.32.202:80",   # Japan
    "http://101.255.118.9:3127",  # Canada
    "http://133.18.234.13:80",     # United States
    "http://130.245.32.202:80",   # United States
    "http://132.148.167.243:2197", # Vietnam
    "http://101.101.217.36:80",     # United States
    "http://13.103.198.233:80"   # United States
]

# User-Agent list
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.62 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.111 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1"
]

# Selenium setup
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    return driver

def use_session_cookie(driver, session_id):
    """Use a session ID to log in to LinkedIn."""
    logging.info("Using session ID to authenticate")
    driver.get('https://www.linkedin.com')  # Open LinkedIn home page

    # Add session cookie
    driver.add_cookie({
        'name': 'li_at',
        'value': session_id,
        'domain': '.linkedin.com'
    })

    # Refresh the page to apply the session
    driver.refresh()

def login_to_linkedin(driver):
    driver.get("https://www.linkedin.com")
    logging.info("Logging in with session ID.")
    print("Initial cookies:", driver.get_cookies())
    use_session_cookie(driver, SESSION_ID)
    print("Cookies after adding session ID:", driver.get_cookies())
    driver.get("https://www.linkedin.com/feed/")

# Extract profile data
def extract_profile_data(driver, url):
    logging.info(f"Scraping profile data from {url}")
    driver.get(url)
    time.sleep(3)  # Wait for the page to load

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')

    profile_data = {}

    name = soup.find('h1', {'class': 'text-heading-xlarge'})
    if name:
        profile_data['name'] = name.get_text().strip()

    headline = soup.find('div', {'class': 'text-body-medium break-words'})
    if headline:
        profile_data['headline'] = headline.get_text().strip()

    about_section = soup.find('div', {'class': 'display-flex ph5 pv3'})
    if about_section:
        profile_data['about'] = about_section.get_text().strip()

    # # Update for the about section
    # about_section = soup.find('div', {'class': 'display-flex ph5 pv3'})
    # if about_section:
    #     try:
    #         # Click the "see more" button to expand the about section
    #         driver.find_element(By.CLASS_NAME, "inline-show-more-text__button").click()
    #         time.sleep(2)  # Allow time for the content to load
    #         page_source = driver.page_source
    #         soup = BeautifulSoup(page_source, 'lxml')
    #         about_section = soup.find('div', {'class': 'display-flex ph5 pv3'})
    #         about = about_section.get_text().strip() if about_section else None
    #         profile_data['about'] = about
    #     except Exception as e:
    #         logging.warning(f"Unable to expand 'About' section: {e}")
    #         profile_data['about'] = about_section.get_text().strip()


    experience_section = soup.find('section', {'id': 'experience-section'})
    if experience_section:
        experience_items = experience_section.find_all('li')
        profile_data['experience'] = [item.get_text(strip=True) for item in experience_items]

    # Updated experience section logic
    # sections = soup.find_all('section', {'class': 'artdeco-card pv-profile-card break-words mt2'})
    # for sec in sections:
    #     if sec.find('div', {'id': 'experience'}):
    #         experience_section = sec
    #         break
    # else:
    #     experience_section = None

    # if experience_section:
    #     experience_items = experience_section.find_all('li')
    #     profile_data['experience'] = [item.get_text(strip=True) for item in experience_items]

    education_section = soup.find('section', {'id': 'education-section'})
    if education_section:
        education_items = education_section.find_all('li')
        profile_data['education'] = [
            {
                'college': item.find('span', {'class': 'visually-hidden'}).get_text(strip=True),
                'degree': item.find('span', {'class': 'degree-name'}).get_text(strip=True) if item.find('span', {'class': 'degree-name'}) else None,
                'duration': item.find('time').get_text(strip=True) if item.find('time') else None
            }
            for item in education_items
        ]

    return profile_data

# Helper functions for content processing
def extract_body_content(html_content):
    """Extract the body content from HTML."""
    soup = BeautifulSoup(html_content, "html.parser")
    print("Before cleaning, content:")
    print(html_content[:500])  # Print the first 500 characters for brevity
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""

def clean_body_content(body_content):
    """Clean the body content by removing scripts and styles."""
    soup = BeautifulSoup(body_content, "html.parser")
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()
    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )
    print("After cleaning, cleaned content:")
    print(cleaned_content[:500])  # Print the first 500 characters for brevity
    return cleaned_content

def split_dom_content(dom_content, chunk_size=500):
    """Split the DOM content into chunks of specified size."""
    words = dom_content.split()
    return [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
