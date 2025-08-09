import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

HEADERS = {'User-Agent': 'Mozilla/5.0'}

def parse_price(text):
    nums = re.sub(r'\D', '', text)
    return int(nums) if nums else None

def extract_id_from_url(url):
    match = re.search(r'/(\d+)', url)
    return match.group(1) if match else url

def fetch_all_sites(max_price=3000):
    urls = [
        'https://autodiler.me/ru/avtomobili/poisk?pageNumber=1&formStyle=detail&brandsText=&country=1&cityText=&locationText=&sortBy=dateDesc&price=[null%2C"3000"]',
        'https://www.autodiler.me/ru/avtomobili/'
    ]

    ads = []

    for url in urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')

            for item in soup.select('.oglasi-item-tekst-oglasi, .oglasi-item-tekst-avtomobili'):
                title_tag = item.select_one('a.oglasi-item-heading > h3')
                link_tag = item.select_one('a.oglasi-item-heading')
                price_tag = item.select_one('.cena p')
                location_tag = item.select_one('.oglasi-items-tekst-lokacija .oglasi-mesto p')
                km_tag = item.select_one('li span[title="Пробег"] + span')
                year_tag = item.select_one('li span[title="Год выпуска"] + span')
                img_tag = item.select_one('.oglasi-item-tekst-img img')

                if not (title_tag and link_tag and price_tag):
                    continue

                link = urljoin(url, link_tag['href'])
                ad_id = extract_id_from_url(link)

                title = title_tag.get_text(strip=True)
                price = parse_price(price_tag.get_text())
                location = location_tag.get_text(strip=True) if location_tag else "Не указано"
                km = km_tag.get_text(strip=True) if km_tag else "Не указано"
                year = year_tag.get_text(strip=True) if year_tag else "Не указано"
                image_url = img_tag['src'] if img_tag else None

                if price and price <= max_price:
                    ads.append({
                        'id': ad_id,
                        'title': title,
                        'price': price,
                        'url': link,
                        'location': location,
                        'km': km,
                        'year': year,
                        'image_url': image_url
                    })
        except Exception as e:
            print(f"Ошибка при парсинге {url}: {e}")

    return ads

