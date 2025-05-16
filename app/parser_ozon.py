from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time

def parse_ozon(url):
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)

    try:
        driver.get(url)
        time.sleep(5)  # Ждем загрузки страницы

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        title = soup.find('h1').get_text(strip=True)
        price_element = soup.find('span', {'data-test-id': 'product-price-current'})
        price = price_element.get_text(strip=True) if price_element else 'Цена не найдена'

        return {'title': title, 'price': price}
    finally:
        driver.quit()
