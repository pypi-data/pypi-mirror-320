# morph_extractor/wiktionary_loader.py

import signal
import logging

from langchain_community.document_loaders import PlaywrightURLLoader

logger = logging.getLogger(__name__)

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Timeout reached while loading page via Playwright.")





from langchain_community.document_loaders import AsyncPlaywrightURLLoader
import logging

logger = logging.getLogger(__name__)

from playwright.async_api import async_playwright
import logging

logger = logging.getLogger(__name__)

async def fetch_wiktionary_page_playwright_async(word: str) -> str:
    """
    Loads the Wiktionary page for the given word using Playwright (async).
    Returns rendered text or an empty string if load fails.
    """
    lower_word = word.lower()
    url = f"https://en.wiktionary.org/wiki/{lower_word}"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)
            content = await page.content()
            await browser.close()
            return content
    except Exception as e:
        logger.error(f"Error loading page with Playwright: {e}")
        return ""

'''
def fetch_wiktionary_page_playwright(word: str) -> str:
    """
    Loads the Wiktionary page for the given word using Playwright.
    Returns rendered text or an empty string if load fails.
    """
    lower_word = word.lower()
    url = f"https://en.wiktionary.org/wiki/{lower_word}"

    loader = PlaywrightURLLoader(
        urls=[url],
        remove_selectors=["style", "script"]
    )

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)  # 30-second timeout

    try:
        docs = loader.load()
        signal.alarm(0)
        if not docs:
            logger.warning(f"No docs returned for {url}")
            return ""
        return docs[0].page_content
    except TimeoutException:
        logger.error(f"Timeout loading page for {url}")
        return ""
    except Exception as e:
        logger.error(f"Error loading page with Playwright: {e}")
        return ""
'''