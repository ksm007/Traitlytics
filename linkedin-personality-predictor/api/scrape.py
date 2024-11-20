import asyncio
import logging
import random
import cloudscraper
from bs4 import BeautifulSoup
from pyppeteer import launch
from annoy import AnnoyIndex


# Configure logging
logging.basicConfig(level=logging.INFO)

# List of proxies and user agents for rotation
proxies = [
    "http://102.134.130.41:80", "http://44.195.247.145:80",
    "http://54.233.119.172:3128", "http://3.122.84.99:3128",'http://133.18.234.13'
    # Additional proxies as needed
]

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
    # Additional user agents as needed
]

def scrape_website(website_url, max_retries=3):
    """Scrape the website content using Cloudscraper or fallback to Pyppeteer."""
    attempt = 0
    while attempt < max_retries:
        proxy = random.choice(proxies)
        user_agent = random.choice(user_agents)
        logging.info(f"Attempt {attempt + 1}: Using proxy {proxy} and user agent {user_agent}")

        # Set up Cloudscraper with proxy and user agent
        try:
            scraper = cloudscraper.create_scraper()
            scraper.proxies = {"http": proxy, "https": proxy}
            scraper.headers.update({"User-Agent": user_agent})
            response = scraper.get(website_url, timeout=15, verify=False)
            if response.status_code == 200:
                logging.info("Cloudscraper successfully retrieved the page.")
                return response.text
            else:
                logging.warning(f"Cloudscraper failed with status code: {response.status_code}")
        except Exception as e:
            logging.error(f"Cloudscraper error: {e}")

        # Fallback to Pyppeteer
        try:
            html_content = asyncio.run(scrape_with_puppeteer(website_url, proxy, user_agent))
            if html_content:
                logging.info("Pyppeteer successfully retrieved the content.")
                return html_content
            else:
                logging.warning("Pyppeteer failed to retrieve content.")
        except Exception as e:
            logging.error(f"Pyppeteer error: {e}")

        attempt += 1
        logging.info("Retrying with a new proxy and user agent...")
    return None

async def scrape_with_puppeteer(website_url, proxy, user_agent, timeout=30):
    """Scrape the website content using Pyppeteer with rotating proxies and user agents."""
    browser = None
    try:
        browser = await launch(
            headless=True,
            args=[f'--proxy-server={proxy}'],
            handleSIGINT=False,
            handleSIGTERM=False,
            handleSIGHUP=False,
            ignoreHTTPSErrors=True  # Ignore SSL errors
        )
        page = await browser.newPage()
        await page.setUserAgent(user_agent)
        await page.goto(website_url, waitUntil='networkidle2', timeout=timeout * 1000)
        await page.waitForSelector('body', timeout=timeout * 1000)  # Ensure page body is loaded
        html_content = await page.content()
        return html_content
    except Exception as e:
        logging.error(f"Pyppeteer error: {e}")
        return None
    finally:
        if browser:
            await browser.close()

def extract_body_content(html_content):
    """Extract the body content from HTML."""
    soup = BeautifulSoup(html_content, "html.parser")
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
    return cleaned_content

def split_dom_content(dom_content, chunk_size=500):
    """Split the DOM content into chunks of specified size."""
    words = dom_content.split()
    return [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

def generate_embeddings(chunks, embedding_model):
    """Generate embeddings for the given chunks using the embedding model."""
    embeddings = embedding_model.encode(
        chunks,
        convert_to_numpy=True,
        batch_size=8  # Adjust batch size as needed
    )
    return embeddings

def store_embeddings(embeddings):
    """Store embeddings in an Annoy index for efficient retrieval."""
    dimension = embeddings.shape[1]
    index = AnnoyIndex(dimension, 'angular')
    for i, vector in enumerate(embeddings):
        index.add_item(i, vector)
    index.build(10)  # Number of trees
    return index

def retrieve_relevant_chunks(query, index, chunks, embedding_model, top_k=5):
    """Retrieve the top_k relevant chunks for the query."""
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    indices = index.get_nns_by_vector(
        query_embedding[0], top_k, include_distances=False)
    relevant_chunks = [chunks[i] for i in indices]
    return relevant_chunks
