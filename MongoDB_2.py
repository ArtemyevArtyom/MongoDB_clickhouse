import requests
import re
import json
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from pprint import pprint

ua = UserAgent()
headers = {"User-Agent": ua.chrome}
# headers = {"User-Agent": ua.random}
# params = {'page': 1}
session = requests.session()

# извлечь информацию о всех книгах на сайте во всех категориях:
# название, цену, количество товара в наличии
all_books = []
url = "http://books.toscrape.com/"
url_add = ""
end_page = True
while end_page:
    try:
        url_new = url + url_add
        # Запрос основной веб-страницы 
        response = session.get(url_new, headers=headers)

        # Парсинг HTML-содержимого веб-страницы с помощью Beautiful Soup
        soup = BeautifulSoup(response.text, "html.parser")
        try:
            url_add = soup.find('li', {'class': 'next'}).findChildren()[0].get('href')
            if 'catalogue' not in url_add:
                url_add = 'catalogue/' + url_add
        except:
            end_page = False
        books = soup.find_all('li', {'class': 'col-xs-6'})

        for book in books:
            book_info = {}
            # название
            name_info = book.find('h3').findChildren()[0]
            book_info['name'] = name_info.get('title')
            href = name_info.get('href')
            if 'catalogue' in href:
                book_info['url'] = url + href
            else:
                book_info['url'] = url + 'catalogue/' + href

            # цену
            # в формате integer, описание
            price_info = book.find('div', {'class': 'product_price'}).findChildren()[0].getText()[1:]
            book_info['price'] = [float(price_info[1:]),
                                  price_info[0]]
            # количество товара в наличии 
            # в формате integer, описание
            # Запрос веб-страницы книги
            response = session.get(book_info['url'], headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            avail_info = soup.find('p', {'class': 'instock availability'}).getText()
            book_info['avail'] = [int(re.findall('\d+', avail_info)[0]),
                                  re.sub("^\s+|\n|\r|\s+$", '', avail_info)]

            # Извлечение данных и сохранение их в списке словарей
            all_books.append(book_info)
            # и в списке URL-адресов
            # all_url.append(book_info['url'])
            print(book_info['name'])
        if end_page:
            print(f"\nСтраница {url_add}")
    except:
        # pprint(all_books)
        print()
        break

# сохранение данных в JSON-файл
with open('books_data.json', 'w') as f:
    json.dump(all_books, f)
