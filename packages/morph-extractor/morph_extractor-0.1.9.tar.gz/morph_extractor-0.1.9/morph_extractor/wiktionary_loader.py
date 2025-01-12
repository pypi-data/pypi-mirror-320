'''# morph_extractor/wiktionary_loader.py
import openai
import logging
import asyncio

from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

def fetch_wiktionary_page_playwright(word: str) -> str:
    """
    Public function that your codebase calls.
    Internally runs the async function via asyncio.run().
    """
    return asyncio.run(_fetch_wiktionary_page_async(word))

async def _fetch_wiktionary_page_async(word: str) -> str:
    """
    Loads the Wiktionary page for the given word using Playwright's Async API.
    Returns rendered HTML or an empty string if an error occurs.
    """
    lower_word = word.lower()
    url = f"https://en.wiktionary.org/wiki/{lower_word}"

    # 30-second timeout can be enforced by specifying a timeout in milliseconds
    # in the calls to .goto(...) or the browser context. 
    # Alternatively, you can use asyncio.wait_for(...) if you want a hard cutoff.
    timeout_ms = 30000

    try:
        async with async_playwright() as p:
            # Launch a headless browser (Chromium by default).
            browser = await p.chromium.launch()
            page = await browser.new_page()

            # Navigate to the page
            await page.goto(url, timeout=timeout_ms)

            # You can wait for specific content, or just wait a bit for the page to load
            # e.g. await page.wait_for_timeout(1000)

            # Extract rendered content
            content = await page.content()
            await browser.close()

            return content or ""
    except asyncio.TimeoutError:
        logger.error(f"Timeout reached while loading {url}")
        return ""
    except Exception as e:
        logger.error(f"Error loading page with Playwright: {e}")
        return ""
'''



# morph_extractor/wiktionary_loader.py
import openai
import signal
import logging

from langchain_community.document_loaders import PlaywrightURLLoader

logger = logging.getLogger(__name__)

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Timeout reached while loading page via Playwright.")

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
