import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = 'https://brickset.com'
PARTS_URL = f'{BASE_URL}/browse/parts'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

def get_soup(url):
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return BeautifulSoup(response.content, 'html.parser')

def scrape_platforms():
    soup = get_soup(PARTS_URL)
    platforms = []
    navrows = soup.find_all('section', class_='navrow')
    for navrow in navrows:
        links = navrow.find_all('a')
        for link in links:
            platform_name = link.text.strip().split(' (')[0]
            platform_url = BASE_URL + link['href']
            platforms.append({'name': platform_name, 'url': platform_url})
    return platforms

def scrape_bricks(platform):
    bricks = []
    page = 1
    while True:
        print(f'Scraping {platform["name"]} bricks, page {page}')
        url = f'{platform["url"]}/page-{page}'
        soup = get_soup(url)
        brick_elements = soup.find_all('article', class_='set')
        if not brick_elements:
            break
        for brick_element in brick_elements:
            brick_info = {}
            brick_info['name'] = brick_element.select_one('.meta h1 a').text.strip()
            brick_info['part_number'] = brick_element.select_one('.tags a').text.strip()
            brick_info['image_url'] = brick_element.select_one('.mainimg img')['src']
            tags = brick_element.select_one('.tags').find_all('a')
            brick_info['tags'] = [tag.text for tag in tags]
            bricks.append(brick_info)
        page += 1
        time.sleep(1)  # To avoid hitting rate limits
    return bricks

def save_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def scrape_all_bricks():
    all_bricks = []
    platforms = scrape_platforms()
    for platform in platforms:
        bricks = scrape_bricks(platform)
        all_bricks.extend(bricks)
    save_json(all_bricks, 'lego_bricks.json')
    print(f'Saved {len(all_bricks)} bricks to lego_bricks.json')

if __name__ == '__main__':
    scrape_all_bricks()
