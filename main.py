from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

import requests


def check_majority(driver):
    switch_label = driver.find_element(By.CSS_SELECTOR, 'label.agree-switcher')
    switch_label.click()


def set_needed_price(driver, min_price, max_price):
    min_price_input = driver.find_elements(By.ID, 'market-filter-minPrice')[0]
    max_price_input = driver.find_elements(By.ID, 'market-filter-minPrice')[1]
    min_price_input.clear()
    max_price_input.clear()
    min_price_input.send_keys(min_price)
    max_price_input.send_keys(max_price)


def load_all_items(driver):
    while True:
        try:
            load_more_btn = WebDriverWait(driver, 1).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '.load-more')))
            load_more_btn.click()
            time.sleep(1)
        except:
            break


def start_looking_items_in_steam_market(items, items_game):
    top_prices = {}
    for item in items:
        key = f"{item['title']} | {item['subtitle']}"
        if items_game == 'csgo':
            if item['wear'] in wears:
                url = f"https://steamcommunity.com/market/priceoverview/?appid=730&currency=1&market_hash_name={item['title']} | " \
                      f"{item['subtitle']} ({englishWears[item['wear']]})"
            else:
                url = f"https://steamcommunity.com/market/priceoverview/?appid=730&currency=1&market_hash_name={item['title']} | " \
                      f"{item['subtitle']}"
        elif items_game == 'dota':
            url = 'https://steamcommunity.com/market/priceoverview/?appid=570&currency=1' \
                  f"&market_hash_name={item['title']}"
        while True:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data is not None:
                    try:
                        run_price = float(item['price'].replace('$', ''))
                        steam_price = float(data['lowest_price'].replace('$', ''))
                        difference_in_percents = round(((steam_price - run_price) / run_price) * 100, 1)
                        price_info = f'Цены: {run_price} $ => {steam_price} $ | {difference_in_percents}%'
                        if items_game == 'dota':
                            print(item['title'])
                            print(price_info, '\n')
                        elif items_game == 'csgo':
                            print(item['title'], '|', item['subtitle'],
                                  f'({item["wear"]})' if item['wear'] in wears else '')
                            print(price_info, '\n')

                            result_string = ""

                            top_prices[key] = difference_in_percents

                            if len(top_prices) > 20:
                                min_key = min(top_prices, key=top_prices.get)
                                del top_prices[min_key]

                            sorted_top_prices = sorted(top_prices.items(), key=lambda x: x[1], reverse=True)

                            for item_name, diff in sorted_top_prices:
                                result_string += f"{item_name} => {diff}% \n"

                            # print(result_string)

                            with open("Log.txt", "w", encoding='utf-8') as file:
                                file.write(f"{result_string}\n")
                            break
                    except Exception:
                        print('Не удалось получить lowest_price для', url, '\n')
                        break
                else:
                    print('API вернул null, повторяем через 5 секунд\n')
                    time.sleep(5)
            elif response.status_code == 429:
                print(f"Ошибка запроса: {response.status_code} \n {url}")
                print("Получен код ошибки 429. Ждём минутку и продолжаем кошмарить сервер ^) \n")
                time.sleep(60)
            else:
                print(f"Ошибка запроса: {response.status_code} \n {url} \n")
                break
        time.sleep(0.2)


min_price = input("Минимальная сумма: ")
max_price = input("Максимальная сумма: ")

chrome_driver_path = './chromedriver.exe'
os.environ['PATH'] += ';' + os.path.dirname(os.path.abspath(chrome_driver_path))

driver = webdriver.Chrome()

driver.get('https://csgo3.run/market/')

wait = WebDriverWait(driver, 3)

check_majority(driver)

set_needed_price(driver, min_price, max_price)

load_all_items(driver)

# driver.implicitly_wait(3)

drop_preview_elements = driver.find_elements(By.CLASS_NAME, 'drop-preview')

print("Количество товаров:", len(drop_preview_elements))
print('\n', '_______________________')

items = []

for card in drop_preview_elements:
    price_el = card.find_element(By.CLASS_NAME, 'drop-preview__price')
    title_el = card.find_element(By.CLASS_NAME, 'drop-preview__title')
    subtitle_el = card.find_element(By.CLASS_NAME, 'drop-preview__subtitle')
    desc_el = card.find_element(By.CLASS_NAME, 'drop-preview__desc')

    item_data = {
        "price": price_el.text,
        "title": title_el.text,
        "subtitle": subtitle_el.text,
        "wear": desc_el.text
    }

    items.append(item_data)

    print("Цена:", item_data["price"])
    print("Название:", item_data["title"])
    print("Износ:", item_data["wear"])
    print('_______________________')

driver.quit()

wears = [
    'Прямо с завода',
    'Немного поношенное',
    'После полевых',
    'Поношенное',
    'Закалённое в боях'
]

englishWears = {
    'Прямо с завода': 'Factory New',
    'Немного поношенное': 'Minimal Wear',
    'После полевых': 'Field-Tested',
    'Поношенное': 'Well-Worn',
    'Закалённое в боях': 'Battle-Scarred'
}

csgo_items = []
rust_items = []
dota_items = []

for item in items:
    if item['title'] != '' and item['subtitle'] == '' and item['wear'] != '':
        dota_items.append(item)
    elif item['title'] != '' and item['subtitle'] == '' and item['wear'] == '':
        if item['title'] == 'Engineer SMG':
            rust_items.append(item)
    else:
        csgo_items.append(item)

print(csgo_items, '\n', '___________')
print(dota_items, '\n', '___________')
print(rust_items, '\n', '___________')

start_looking_items_in_steam_market(csgo_items, 'csgo')
start_looking_items_in_steam_market(dota_items, 'dota')
