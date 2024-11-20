import asyncio
import logging
import random
import cloudscraper
from bs4 import BeautifulSoup
from pyppeteer import launch
from annoy import AnnoyIndex
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(level=logging.INFO)

# List of proxies and user agents for rotation
proxies = [
    "http://102.134.130.41:80",
    "http://44.195.247.145:80",
    "http://54.233.119.172:3128",
    "http://3.122.84.99:3128",
    "http://133.18.234.13",
    "http://172.94.32.48:80",    # Singapore
    "http://84.32.230.73:80",    # Lithuania
    "http://91.148.134.48:80",   # Colombia
    "http://20.233.44.207:80",   # United Arab Emirates
    "http://208.104.211.63:80",  # United States
    "http://178.16.130.81:80",   # France
    "http://13.80.134.180:80",   # Netherlands
    "http://51.75.33.162:80",    # Poland
    "http://64.92.82.58:8080",   # United States
    "http://160.86.242.23:8080", # Japan
    "http://4.157.219.21:80",    # United States
    "http://43.134.68.153:3128", # Singapore
    "http://47.242.47.64:8888",  # Hong Kong
    "http://200.174.198.86:8888",# Brazil
    "http://5.252.22.45:80",     # Germany
    "http://157.254.53.50:80",   # Hong Kong
    "http://46.47.197.210:3128", # Russia
    "http://195.114.209.50:80",  # Spain
    "http://159.203.61.169:3128",# Canada
    "http://43.133.59.220:3128", # Singapore
    "http://5.42.87.139:8080"    # Sweden
]


user_agents = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36",

    # Chrome on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",

    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0",

    # Firefox on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:92.0) Gecko/20100101 Firefox/92.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11.5; rv:91.0) Gecko/20100101 Firefox/91.0",

    # Safari on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",

    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.67",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.961.52 Safari/537.36 Edg/93.0.961.52",

    # Mobile Safari on iOS
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",

    # Chrome on Android
    "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.82 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; Pixel 4 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Mobile Safari/537.36",

    # Opera on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.254",

    # Generic crawler disguises
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)"
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
            headless=False,
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


# old code from LLM SCRAPER

# import asyncio
# import logging

# import cloudscraper
# from bs4 import BeautifulSoup
# from pyppeteer import launch
# from annoy import AnnoyIndex
# from sentence_transformers import SentenceTransformer

# def scrape_website(website_url):
#     """Scrape the website content using Cloudscraper or fall back to Pyppeteer."""
#     # First, try to scrape with Cloudscraper
#     try:
#         scraper = cloudscraper.create_scraper()
#         response = scraper.get(website_url)
#         if response.status_code == 200:
#             print("Cloudscraper successfully retrieved the page.")
#             return response.text
#         else:
#             print(f"Cloudscraper failed with status code: {response.status_code}")
#             # Proceed to Pyppeteer
#     except Exception as e:
#         logging.error(f"Cloudscraper error: {e}")
#         # Proceed to Pyppeteer

#     # If Cloudscraper fails, fallback to Pyppeteer
#     try:
#         html_content = asyncio.run(scrape_with_puppeteer(website_url))
#         if html_content:
#             print("Pyppeteer successfully retrieved the content.")
#             return html_content
#         else:
#             print("Pyppeteer failed to retrieve content.")
#             return None
#     except Exception as e:
#         logging.error(f"Pyppeteer error: {e}")
#         return None

# async def scrape_with_puppeteer(website_url):
#     """Scrape the website content using Pyppeteer."""
#     try:
#         browser = await launch(headless=True)
#         page = await browser.newPage()
#         await page.setUserAgent(
#             'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#             'AppleWebKit/537.36 (KHTML, like Gecko) '
#             'Chrome/58.0.3029.110 Safari/537.36'
#         )
#         await page.goto(website_url, waitUntil='networkidle2')

#         # Check if a common element exists to confirm the page loaded correctly
#         element = await page.querySelector('h1')
#         if element is None:
#             print("Specified element not found, checking page content directly.")
#         else:
#             print("Element found, retrieving content.")

#         html_content = await page.content()
#         if html_content:
#             print("Content found, returning.")
#             return html_content
#         else:
#             print("No content found on the page.")
#             return None
#     except Exception as e:
#         logging.error(f"Pyppeteer error: {e}")
#         return None
#     finally:
#         await browser.close()

# def extract_body_content(html_content):
#     """Extract the body content from HTML."""
#     soup = BeautifulSoup(html_content, "html.parser")
#     body_content = soup.body
#     if body_content:
#         return str(body_content)
#     return ""

# def clean_body_content(body_content):
#     """Clean the body content by removing scripts and styles."""
#     soup = BeautifulSoup(body_content, "html.parser")

#     for script_or_style in soup(["script", "style"]):
#         script_or_style.extract()

#     cleaned_content = soup.get_text(separator="\n")
#     cleaned_content = "\n".join(
#         line.strip() for line in cleaned_content.splitlines() if line.strip()
#     )

#     return cleaned_content

# def split_dom_content(dom_content, chunk_size=500):
#     """Split the DOM content into chunks of specified size."""
#     words = dom_content.split()
#     return [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

# def generate_embeddings(chunks, embedding_model):
#     """Generate embeddings for the given chunks using the embedding model."""
#     embeddings = embedding_model.encode(
#         chunks,
#         convert_to_numpy=True,
#         batch_size=8  # Adjust batch size as needed
#     )
#     return embeddings

# def store_embeddings(embeddings):
#     """Store embeddings in an Annoy index for efficient retrieval."""
#     dimension = embeddings.shape[1]
#     index = AnnoyIndex(dimension, 'angular')
#     for i, vector in enumerate(embeddings):
#         index.add_item(i, vector)
#     index.build(10)  # Number of trees
#     return index

# def retrieve_relevant_chunks(query, index, chunks, embedding_model, top_k=5):
#     """Retrieve the top_k relevant chunks for the query."""
#     query_embedding = embedding_model.encode([query], convert_to_numpy=True)
#     indices = index.get_nns_by_vector(
#         query_embedding[0], top_k, include_distances=False)
#     relevant_chunks = [chunks[i] for i in indices]
#     return relevant_chunks
