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
    url = 'https://m.search.naver.com/search.naver?where=m&sm=mtb_etc&mra=bjZF&qvt=0&query=%ED%8E%B8%EC%9D%98%EC%A0%90%ED%96%89%EC%82%AC'
    driver.get(url)
    time.sleep(5)
    
    found_cu = False
    for p in range(1, 51):
        print(f"Checking Page {p}...")
        products = driver.find_elements(By.CSS_SELECTOR, "ul[role='list'] > li[role='listitem']")
        for product in products:
            try:
                brand = product.find_element(By.CSS_SELECTOR, "span.store_info").text
                if 'CU' in brand.upper():
                    print(f"FOUND CU ITEM on Page {p}!")
                    found_cu = True
                    break
            except:
                pass
        if found_cu: break
        
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a.cmm_pg_next.on")
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(1)
        except:
            break
            
    if not found_cu:
        print("CU not found in 50 pages.")

finally:
    driver.quit()
