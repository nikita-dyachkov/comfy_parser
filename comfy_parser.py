from pydantic import BaseModel
from bs4 import BeautifulSoup
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

MAIN_URL = 'https://comfy.ua/ua/notebook/'
products = []


class Product(BaseModel):
    name: str
    price: str
    link: str

    def __str__(self):
        return f"{self.name} - {self.get_clean_price()} - {self.link}"

    def get_clean_price(self):
        price = ''
        for char in self.price:
            if char.isdigit():
                price += char
        return int(price)


def get_options():
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument("window-size=1920x1080")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    return chrome_options


def get_last_page(url: str = MAIN_URL):
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=get_options())
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    last_page = int(soup.select('.pagination-item')[-2].text.replace(' ', ''))
    driver.quit()
    return last_page


def get_product_data(url: str):
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=get_options())
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    for item in soup.select('.products-list-item'):
        name = item.select_one('.products-list-item__name').text
        price = item.select_one('.products-list-item__actions-price-current').text
        link = item.select_one('a', href=True)['href']
        products.append(Product(name=name, price=price, link=link))
    driver.quit()


if __name__ == '__main__':
    for i in range(get_last_page()):
        url = f'{MAIN_URL}?p={i + 1}'
        get_product_data(url)
    products_sorted_by_price = sorted(products, key=lambda product: product.get_clean_price())
    for product in products_sorted_by_price:
        print(product)
