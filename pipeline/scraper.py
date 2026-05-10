import random
import json
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PWTimeoutError
from playwright_stealth import Stealth
from pathlib import Path
import unicodedata
import re
from logger import logger

BASE_DIR = Path(__file__).parent.parent
POSITIONS_DATA = BASE_DIR / "data" / "positions.json"
PLATY_URL = "https://www.platy.cz/platy"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

async def human_like_interaction(page):
    await page.mouse.move(100, 100)
    await asyncio.sleep(random.uniform(0.5, 1.5))
    await page.mouse.move(200, 300)
    await asyncio.sleep(random.uniform(0.5, 1.5))
    await page.evaluate("window.scrollBy(0, window.innerHeight / 2)")
    await asyncio.sleep(random.uniform(1, 2))


async def scrape_positions():
    async with Stealth().use_async(async_playwright()) as p:
        user_agent = random.choice(USER_AGENTS)
        browser = await p.chromium.launch(headless=True)

        context_kwargs = {
            "viewport": {"width": 1365, "height": 768},
            "java_script_enabled": True,
            "user_agent": user_agent,
        }

        context = await browser.new_context(**context_kwargs)
        page = await context.new_page()
        page.set_default_timeout(60_000)

        try:
            await page.goto(PLATY_URL, wait_until="domcontentloaded")
            try:
                await page.wait_for_load_state("networkidle", timeout=60_000)
            except PWTimeoutError:
                await asyncio.sleep(3)

            await human_like_interaction(page)

            await page.evaluate("document.getElementById('cc-main').remove()")
            await asyncio.sleep(1)

            await page.click(".ts-wrapper")
            await page.wait_for_selector("#cat_pos-ts-dropdown", state="visible")
            positions = {}
            optgroups = await page.query_selector_all("#cat_pos-ts-dropdown .optgroup")

            for group in optgroups:
                header = await group.query_selector(".optgroup-header")
                category = await header.inner_text()

                options = await group.query_selector_all("[role='option']")
                positions[category] = []

                for option in options:
                    name = await option.inner_text()
                    positions[category].append(name.strip())
            return positions

        finally:
            await page.close()
            await context.close()
            await browser.close()

def load_positions():
    try:
        with open(POSITIONS_DATA, "r", encoding="utf-8") as f:
            content = f.read()
            if not content:
                return None
            return json.loads(content)
    except FileNotFoundError:
        return None

async def get_positions():
    positions = load_positions()
    if positions:
        return positions

    positions = await scrape_positions()

    with open(POSITIONS_DATA, "w", encoding="utf-8") as f:
        json.dump(positions, f, ensure_ascii=False, indent=2)

    return positions


def to_slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    return text

def build_url(category: str, position: str) -> str:
    return f"https://www.platy.cz/platy/{to_slug(category)}/{to_slug(position)}?search=1"

def parse_salary(raw: str) -> dict:
    numbers = re.findall(r'\d+', raw)
    return {
        "min": int(numbers[0]) * 1000,
        "max": int(numbers[1]) * 1000,
        "currency": "CZK"
    }

async def scrape_salary(category: str, position: str) -> dict:
    url = build_url(category, position)
    logger.info(f"Scraping URL: {url}")

    async with Stealth().use_async(async_playwright()) as p:
        user_agent = random.choice(USER_AGENTS)
        browser = await p.chromium.launch(headless=True)

        context = await browser.new_context(
            viewport={"width": 1365, "height": 768},
            user_agent=user_agent,
        )
        page = await context.new_page()
        page.set_default_timeout(60_000)

        try:
            await page.goto(url, wait_until="domcontentloaded")
            try:
                await page.wait_for_load_state("networkidle", timeout=60_000)
            except PWTimeoutError:
                await asyncio.sleep(3)

            await human_like_interaction(page)

            await page.evaluate("document.getElementById('cc-main').remove()")
            await asyncio.sleep(1)

            selector = ".range-chart-values"
            await page.wait_for_selector(selector)
            element = await page.query_selector(selector)
            text = await element.inner_text()
            logger.info(f"Salary raw: {text}")

            return {
                "category": category,
                "position": position,
                "url": url,
                "salary": parse_salary(text)
            }

        finally:
            await page.close()
            await context.close()
            await browser.close()