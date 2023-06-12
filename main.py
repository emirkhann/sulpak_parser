import csv
import json

import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag


URL = 'https://www.sulpak.kg/' 


def get_html(url: str, category: str, params: str=''):
    """  
    Функция для получения html кода страницы
    url - ссылка для парсинга
    category - категория с сайта для парсинга
    params - параметры ссылки - '?page=12'
    """
    html = requests.get(
        url=url + 'f/' + category, # формирование ссылки 'https://www.sulpak.kg/' + 'f/' + 'smartfoniy/' -> 'https://www.sulpak.kg/f/smartfoniy/' 
        params=params,
        verify=False
    )
    return html.text


def get_cards_from_html(html: str) -> ResultSet:
    """  
    Функция для получения карточек из html-кода
    """
    soup = BeautifulSoup(html, 'lxml')
    cards = soup.find_all('div', class_='product__item-inner')
    return cards


def parse_data_from_cards(cards: ResultSet) -> list:
    """  
    Функция для парсинга карточек товаров.
    На выходе получаем список из словарей, где каждый словарь
    представляет собой товар

    Поскольку у некоторых карточек отсутствуют некоторые
    данные, то вместо текста метод .find() может вернуть
    None. У None нельзя вызвать .text и python вызовет ошибку
    AttributeError. Обрабатываем этот случай и задаем другое значение
    """
    result = []
    for card in cards:
        try:
            title = card.find('div', class_='product__item-name').text
        except AttributeError:
            title = 'Нет названия'
        try:
            price = card.find('div', class_='product__item-price').text
        except AttributeError:
            price = 'Нет цены'
        try:
            description = card.find('div', class_='product__item-description').text
        except AttributeError:
            description = 'Нет описания'
        try:
            in_stock = card.find('div', class_='product__item-showcase').text
        except AttributeError:
            in_stock = 'Нет в наличии'
        try:
            image_link = card.find('img', class_='image-size-cls').get('src')
        except AttributeError:
            image_link = 'Нет картинки'

        obj = {
            'title': title,
            'price': price,
            'description': description,
            'in_stock': in_stock,
            'image_link': image_link
        }
        result.append(obj)
    return result


def write_to_csv(data: list, file_name: str) -> None:
    """ 
    Функция для записи данных в файл 
    data - данные для записи
    file_name - название файла для записи
    """
    fieldnames = data[0].keys() # получение ключей словаря для использования в качестве названия столбцов
    with open(f'{file_name}.csv', 'w') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def get_last_page(html: str) -> int:
    """ Функция для получения номера последней страницы """
    soup = BeautifulSoup(html, 'lxml')
    last_page = soup.find('div', class_='pagination').get('data-pagescount')
    return int(last_page)



def main() -> None:
    """ 
    Функция main(), которая запускает все остальные функции,
    которые определены выше. Нужна для того, чтобы определить
    порядок вызова функций. 
    """
    result = []
    html = get_html(URL, 'smartfoniy') # получаем html код страницы
    last_page = get_last_page(html) # получаем номер последней страницы
    for page in range(1, last_page+1): # запускаем цикл столько раз, сколько страниц есть на сайте
        html = get_html(URL, 'smartfoniy', params=f'page={page}') # получаем html код страницы с параметром page, чтобы парсинг шел по всем страницам
        cards = get_cards_from_html(html) # получение карточек со страниц
        result_from_page = parse_data_from_cards(cards) # получение списков с данными
        result.extend(result_from_page) # расширяем основной список result данными со всех страниц
    write_to_csv(result, 'smartphones') # записываем конечный результат в файл
    


if __name__ == '__main__':
    """  
    Это условие нужно для того, чтобы определить
    точку входа в программу - место, откуда наша
    программа начинает свою работу
    """
    main()


# TODO: Загрузить этот проект на гитхаб и скинуть ссылку в группу
