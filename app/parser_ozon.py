from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def parse_ozon(url):
    options = Options()
    # Окно будет видно (можно отключить в будущем)
    # options.headless = True
    driver = webdriver.Firefox(options=options)

    try:
        driver.get(url)

        # Ждём появление любого <span>
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, 'span'))
        )

        title = driver.find_element(By.TAG_NAME, 'h1').text.strip()

        price = None
        for el in driver.find_elements(By.TAG_NAME, 'span'):
            text = el.text.strip().replace('\u00a0', '')
            if '₽' in text and any(char.isdigit() for char in text):
                price = float(text.replace('₽', '').replace(',', '.'))
                break

        driver.quit()

        if not title or price is None:
            print("❌ Не удалось получить данные")
            return None

        print(f"✅ Успешно: {title} — {price} ₽")
        return {'title': title, 'price': price}

    except Exception as e:
        driver.quit()
        print("‼️ Ошибка Selenium с Firefox:", e)
        return None
