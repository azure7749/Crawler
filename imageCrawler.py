import asyncio
import aiohttp
from bs4 import BeautifulSoup
import os

# Base URL of the website to start scraping
base_url = 'http://publicdomain.tw'
start_url = '/u/pd4pd/m/Da-Ban-Lei/'
image_directory = 'downloaded_images'

# Ensure the image directory exists
os.makedirs(image_directory, exist_ok=True)

async def fetch(session, url):
    async with session.get(base_url + url) as response:
        if response.status != 200:
            print(f"Failed to retrieve page: {url}")
            return None
        return await response.text()

async def download_image(session, url, image_name):
    async with session.get(url) as response:
        if response.status != 200:
            print(f"Failed to download image: {url}")
            return
        image_path = os.path.join(image_directory, image_name)
        with open(image_path, 'wb') as f:
            f.write(await response.read())
        print(f"Downloaded image: {image_path}")

async def scrape_images(session, url):
    html_content = await fetch(session, url)
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, 'html.parser')
    image_container = soup.find('div', class_='media_image_container')
    if image_container:
        image_tag = image_container.find('a')
        if image_tag:
            image_url = base_url + image_tag['href']
            image_name = image_url.split('/')[-1]
            await download_image(session, image_url, image_name)

async def find_next_page(session, url):
    html_content = await fetch(session, url)
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, 'html.parser')
    nav_button = soup.find('a', class_='navigation_button navigation_right')
    if nav_button:
        return nav_button['href']
    return None

async def main():
    async with aiohttp.ClientSession() as session:
        current_url = start_url

        while current_url:
            tasks = [scrape_images(session, current_url), find_next_page(session, current_url)]
            _, next_page = await asyncio.gather(*tasks)

            if not next_page:
                print("No more pages to scrape.")
                break

            current_url = next_page

if __name__ == '__main__':
    asyncio.run(main())
