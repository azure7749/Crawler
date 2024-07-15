import asyncio
import aiohttp
from bs4 import BeautifulSoup
import csv

# Base URL of the website to start scraping
base_url = 'http://publicdomain.tw'
start_url = '/u/pd4pd/m/Da-Ban-Lei/'


async def fetch(session, url):
    async with session.get(base_url + url) as response:
        if response.status != 200:
            print(f"Failed to retrieve page: {url}")
            return None
        return await response.text()


async def scrape_metadata(session, url):
    html_content = await fetch(session, url)
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, 'html.parser')
    metadata_table = soup.find('table', class_='metadata_info')
    if metadata_table:
        metadata = {}
        for row in metadata_table.find_all('tr'):
            key = row.find('th').text.strip()
            value = row.find('td').text.strip()
            metadata[key] = value
        return metadata
    return None


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
        all_metadata = []

        while current_url:
            tasks = [scrape_metadata(session, current_url), find_next_page(session, current_url)]
            metadata, next_page = await asyncio.gather(*tasks)

            if metadata:
                all_metadata.append(metadata)
                print(f"Scraped metadata from {current_url}")

            if not next_page:
                print("No more pages to scrape.")
                break

            current_url = next_page

        # Save all metadata to a CSV file
        if all_metadata:
            keys = all_metadata[0].keys()
            with open('metadata.csv', 'w', newline='', encoding='utf-8') as output_file:
                dict_writer = csv.DictWriter(output_file, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(all_metadata)
            print("Metadata saved to metadata.csv")


if __name__ == '__main__':
    asyncio.run(main())
