import os
import asyncio
from playwright.async_api import async_playwright

async def scrape_usernames(url):
    screenshots_dir = "screenshots"
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)

    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.firefox.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
            locale='ru-RU',
            timezone_id='Europe/Moscow'
        )
        page = await context.new_page()
        print(f"Loading page {url}")
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(3)

        if await page.locator('altcha-widget, .altcha').count() > 0:
            print("\nCAPTCHA detected! Solve it manually and press Enter...")
            input()
            await asyncio.sleep(2)

        usernames_seen = set()
        screenshot_count = 0
        current_page = 1

        while True:
            print(f"Processing page {current_page}...")
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1)
            username_elements = await page.locator('a.username').all()

            for element in username_elements:
                try:
                    username_text = (await element.text_content()).strip()
                    if username_text and username_text not in usernames_seen:
                        usernames_seen.add(username_text)
                        screenshot_count += 1
                        screenshot_path = os.path.join(screenshots_dir, f"{screenshot_count}.jpeg")
                        await element.screenshot(path=screenshot_path, type="jpeg")
                        print(f"Screenshot {screenshot_count}: {username_text}")
                except:
                    continue

            next_page_num = current_page + 1
            next_found = False
            for selector in [f'a[href*="page-{next_page_num}"]', 'a.pageNav-jump--next', 'a[rel="next"]']:
                try:
                    next_button = page.locator(selector).first
                    if await next_button.count() > 0 and await next_button.is_visible():
                        print(f"Moving to page {next_page_num}...")
                        await next_button.click()
                        await asyncio.sleep(3)
                        current_page += 1
                        next_found = True
                        break
                except:
                    continue

            if not next_found:
                break

        print(f"\nTotal {screenshot_count} unique usernames")
        await browser.close()

async def main():
    print("""
 ██████╗ ███╗   ██╗██╗   ██╗██╗  ██╗
██╔═══██╗████╗  ██║╚██╗ ██╔╝╚██╗██╔╝
██║   ██║██╔██╗ ██║ ╚████╔╝  ╚███╔╝
██║   ██║██║╚██╗██║  ╚██╔╝   ██╔██╗
╚██████╔╝██║ ╚████║   ██║   ██╔╝ ██╗
 ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝
    """)
    url = input("\nEnter lolz.live thread URL: ").strip()

    if not url.startswith("https://lolz.live/threads/"):
        print("Invalid URL")
        return

    await scrape_usernames(url)
    print("\nDone!")

if __name__ == "__main__":
    asyncio.run(main())