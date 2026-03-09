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
# PC User Agent
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    # On PC, the URL might be different or the same
    url = 'https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query=%ED%8E%B8%EC%9D%98%EC%A0%90%ED%96%89%EC%82%AC'
    driver.get(url)
    time.sleep(5)
    
    print('--- PC View Results ---')
    # Look for brand chips or table
    try:
        tabs = driver.find_elements(By.CSS_SELECTOR, "ul.tab_list li a span")
        print(f"Tabs found: {[t.text for t in tabs]}")
        
        products = driver.find_elements(By.CSS_SELECTOR, "ul[role='list'] > li[role='listitem']")
        print(f"Products found: {len(products)}")
        
        # Check brand filter
        brands = driver.find_elements(By.CSS_SELECTOR, "a.fds-image-body-basic-chip-anchor, select.slct option")
        print(f"Brands found: {list(set([b.text for b in brands if b.text]))}")
    except:
        print("Table not found on PC view.")

finally:
    driver.quit()
