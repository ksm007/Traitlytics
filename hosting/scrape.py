
import logging
import time
import warnings
from selenium import webdriver
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Session ID for LinkedIn login
SESSION_ID = 'AQEDATD5GXwE5GoFAAABk4pptCIAAAGT1lWhQU0AJIkW8uW6U2Pl4NfzgKEXPvtDBZsFqd28655XQfqvVXYR4qM4moHGWNzPZIqxVmsW6hRRUa623DdQqEmUN37ahRwa-bCDrLrGhwndEpdWpVvJyZHw'

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Suppress warnings
warnings.filterwarnings("ignore")

# Load environment variables
load_dotenv()


def get_driver():
    """Initialize and configure the Selenium WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")  # Enables headless mode

    

    driver = webdriver.Chrome(options=options)
    return driver


def use_session_cookie(driver, session_id):
    """Authenticate LinkedIn using a session cookie."""
    logging.info("Authenticating with session ID.")
    driver.get('https://www.linkedin.com')  # Open LinkedIn home page
    driver.add_cookie({
        'name': 'li_at',
        'value': session_id,
        'domain': '.linkedin.com'
    })
    driver.refresh()


def login_to_linkedin(driver):
    """Login to LinkedIn using the session cookie."""
    driver.get("https://www.linkedin.com")
    use_session_cookie(driver, SESSION_ID)
    driver.get("https://www.linkedin.com/feed/")  # Confirm login by navigating to the feed


def scrape_website(url):
    """Scrape the LinkedIn profile data from the provided URL."""
    driver = get_driver()
    try:
        login_to_linkedin(driver)
        logging.info(f"Scraping content from {url}")
        driver.get(url)
        time.sleep(3)  # Wait for the page to load
        return extract_profile_data(driver)
    finally:
        driver.quit()


def extract_profile_data(driver):
    """Extract profile data such as name, headline, about, education, and experience."""
    soup = BeautifulSoup(driver.page_source, 'lxml')
    profile_data = {}

    # Basic Profile Information
    profile_data['name'] = extract_text(soup.find('h1', {'class': 'text-heading-xlarge'}))
    profile_data['headline'] = extract_text(soup.find('div', {'class': 'text-body-medium break-words'}))
    profile_data['about'] = extract_text(soup.find('div', {'class': 'display-flex ph5 pv3'}))

    # Get all sections for education and experience
    sections = soup.find_all('section', {'class': 'artdeco-card pv-profile-card break-words mt2'})

    # Extract Education Section
    profile_data['education'] = extract_section(sections, 'education')

    # Extract Experience Section
    profile_data['experience'] = extract_experience(sections)

    return profile_data


# def extract_text(element):
#     """Extract and strip text from a BeautifulSoup element."""
#     return element.get_text(strip=True) if element else None
def extract_text(element):
    """Extract and strip text from a BeautifulSoup element. Return 'Not provided' if None."""
    return element.get_text(strip=True) if element else "Not provided"



def extract_section(sections, section_id):
    """Extract and return the text of a specific section by ID."""
    for sec in sections:
        if sec.find('div', {'id': section_id}):
            return sec.get_text(strip=True)
    return None


def extract_experience(sections):
    """Extract experience items, remove duplicates, and return them as a list."""
    for sec in sections:
        if sec.find('div', {'id': 'experience'}):
            experience_items = sec.find_all('li')
            # Remove duplicates while preserving order
            return list(dict.fromkeys([item.get_text(strip=True) for item in experience_items]))
    return []



