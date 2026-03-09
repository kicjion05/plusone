from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604.1')

service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    url = "https://m.search.naver.com/search.naver?where=m&query=CU%20%ED%8E%B8%EC%9D%98%EC%A0%90%20%ED%96%89%EC%82%AC"
    driver.get(url)
    time.sleep(5)
    
    print('--- Checking Smart Block Item Structure ---')
    # Let's search for items containing '웅진'
    items = driver.find_elements(By.XPATH, "//*[contains(text(), '웅진')]")
    for item in items:
        if item.is_displayed():
            print(f"Tag: {item.tag_name}, Class: {item.get_attribute('class')}, Text: {item.text}")
            # See parent structure
            parent = item.find_element(By.XPATH, "..")
            print(f"  Parent Tag: {parent.tag_name}, Class: {parent.get_attribute('class')}")
            grandparent = parent.find_element(By.XPATH, "..")
            print(f"  Grandparent Tag: {grandparent.tag_name}, Class: {grandparent.get_attribute('class')}")

finally:
    driver.quit()
