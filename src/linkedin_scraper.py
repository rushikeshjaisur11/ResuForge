"""
Playwright-based LinkedIn job scraper.

Usage (called by Claude skills):
  python src/linkedin_scraper.py
      Reads config.json + .env, scrapes jobs, saves results to jobs.json
"""

import asyncio
import json
import os
import random
import re

from dotenv import load_dotenv
from playwright.async_api import async_playwright


async def _scrape(config: dict, email: str, password: str) -> list:
    jobs = []
    max_jobs = config.get("max_jobs_to_scrape", 20)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # visible so CAPTCHA can be handled
        context = await browser.new_context()
        page = await context.new_page()

        # --- Login ---
        print("  Navigating to LinkedIn login...")
        await page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        await page.fill("#username", email)
        await page.fill("#password", password)
        await page.click('button[type="submit"]')

        # Wait up to 60s for post-login navigation — user may need to solve CAPTCHA/verification
        print("  Waiting for login... (solve any CAPTCHA/verification in the browser window)")
        try:
            await page.wait_for_url(
                re.compile(r"linkedin\.com/(feed|jobs|checkpoint)"),
                timeout=60000,
            )
        except Exception:
            pass  # proceed regardless; we'll check the URL after

        current_url = page.url
        print(f"  Post-login URL: {current_url}")

        # If stuck on checkpoint/verification, give user time to solve it
        if "checkpoint" in current_url or "login" in current_url:
            print("  Security check detected — please complete it in the browser. Waiting 30s...")
            await asyncio.sleep(30)

        await asyncio.sleep(3)

        # --- Jobs search ---
        titles = config.get("job_titles", config.get("job_title", "Software Engineer"))
        if isinstance(titles, str):
            titles = [titles]
        location = config.get("location", "United States")

        collected = 0
        for title in titles:
            if collected >= max_jobs:
                break

            search_url = (
                f"https://www.linkedin.com/jobs/search/"
                f"?keywords={title.replace(' ', '%20')}"
                f"&location={location.replace(' ', '%20')}"
                f"&f_TPR=r86400"  # last 24 hours
                f"&sortBy=DD"
            )
            print(f"  Searching: '{title}'")
            await page.goto(search_url, wait_until="domcontentloaded")
            await asyncio.sleep(3)

            while collected < max_jobs:
                cards = await page.query_selector_all("li.jobs-search-results__list-item")
                if not cards:
                    cards = await page.query_selector_all("[data-job-id]")
                if not cards:
                    print("  [warn] No job cards found on page")
                    break

                for card in cards:
                    if collected >= max_jobs:
                        break
                    try:
                        job = await _extract_job(page, card)
                        if job and not _is_duplicate(jobs, job["job_id"]):
                            jobs.append(job)
                            collected += 1
                            print(f"  Scraped [{collected}/{max_jobs}]: {job['title']} @ {job['company']}")
                    except Exception as e:
                        print(f"  [warn] Failed to extract job: {e}")
                    await _random_delay(0.5, 1.5)

                if collected >= max_jobs:
                    break

                # Try to load next page
                next_btn = await page.query_selector('button[aria-label="View next page"]')
                if next_btn:
                    await next_btn.click()
                    await asyncio.sleep(3)
                    await _random_delay()
                else:
                    # Scroll to load more
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await _random_delay(2, 3)
                    new_cards = await page.query_selector_all("li.jobs-search-results__list-item")
                    if len(new_cards) <= len(cards):
                        break  # no new jobs on this search

        await browser.close()
    return jobs


async def _extract_job(page, card) -> dict | None:
    """Click a job card and extract structured data."""
    # Try to get job_id and basic info from the card before clicking
    job_id = await card.get_attribute("data-job-id") or ""
    title = ""
    company = ""

    # Try to extract title/company from card's inner HTML via JS
    card_html = await card.evaluate("el => el.innerHTML")

    # Title: look for job title link or aria-label
    title_match = re.search(
        r'aria-label="([^"]+)"[^>]*>(?:[^<]*<[^>]+>)*[^<]*(?:Engineer|Developer|Analyst|Manager|Scientist|Architect|Lead|Consultant|Specialist)',
        card_html,
    )
    if not title_match:
        # Fallback: look for text in title-like elements
        for sel in [
            ".artdeco-entity-lockup__title",
            ".job-card-list__title",
            "a[class*='title']",
            "strong",
        ]:
            try:
                t = (await card.inner_text(sel, timeout=500)).strip()
                if t and len(t) < 120:
                    title = t
                    break
            except Exception:
                pass

    for sel in [
        ".artdeco-entity-lockup__subtitle",
        ".job-card-container__company-name",
        ".job-card-container__primary-description",
        "span[class*='company']",
    ]:
        try:
            c = (await card.inner_text(sel, timeout=500)).strip()
            if c and len(c) < 100:
                company = c
                break
        except Exception:
            pass

    # Click to open job details
    await card.click()
    await asyncio.sleep(2)

    # Refine job_id from URL
    url = page.url
    m = re.search(r"currentJobId=(\d+)", url) or re.search(r"/jobs/view/(\d+)/", url)
    if m:
        job_id = m.group(1)

    if not job_id:
        return None

    # Fallback title/company from the detail panel
    if not title:
        title = await _try_selectors(page, [
            "h1.job-details-jobs-unified-top-card__job-title",
            ".job-details-jobs-unified-top-card__job-title h1",
            ".jobs-unified-top-card__job-title h1",
            "h1.t-24",
            ".artdeco-entity-lockup__title h1",
        ])

    if not company:
        company = await _try_selectors(page, [
            ".job-details-jobs-unified-top-card__company-name a",
            ".job-details-jobs-unified-top-card__company-name",
            ".jobs-unified-top-card__company-name a",
            ".jobs-unified-top-card__company-name",
            "a[data-tracking-control-name='public_jobs_topcard-org-name']",
        ])

    # Job description
    jd_text = await _try_selectors(page, [
        ".jobs-description__content",
        ".jobs-description",
        "#job-details",
        ".job-details-jobs-unified-top-card__primary-description-container",
    ])

    return {
        "job_id": job_id.strip(),
        "title": title.strip(),
        "company": re.sub(r"\s+", " ", company).strip(),
        "full_jd_text": jd_text.strip(),
        "url": url,
    }


async def _try_selectors(page, selectors: list) -> str:
    """Try each selector in order; return first non-empty result."""
    for sel in selectors:
        try:
            text = (await page.inner_text(sel, timeout=2000)).strip()
            if text:
                return text
        except Exception:
            pass
    return ""


def _is_duplicate(jobs: list, job_id: str) -> bool:
    return any(j["job_id"] == job_id for j in jobs)


async def _random_delay(min_s: float = 1.0, max_s: float = 2.5):
    await asyncio.sleep(random.uniform(min_s, max_s))


def scrape_jobs(config: dict, email: str, password: str) -> list:
    """Synchronous entry point."""
    return asyncio.run(_scrape(config, email, password))


if __name__ == "__main__":
    load_dotenv()
    email = os.getenv("LINKEDIN_EMAIL", "")
    password = os.getenv("LINKEDIN_PASSWORD", "")
    if not email or not password:
        raise SystemExit("[error] LINKEDIN_EMAIL and LINKEDIN_PASSWORD must be set in .env")

    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)

    titles = config.get("job_titles", config.get("job_title", ""))
    if isinstance(titles, str):
        titles = [titles]
    print(f"Scraping LinkedIn for {titles} in '{config['location']}'...")
    jobs = scrape_jobs(config, email, password)

    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(jobs)} jobs to jobs.json")
