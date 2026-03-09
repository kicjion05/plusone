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
    brand_urls = {
        'CU': 'https://m.search.naver.com/search.naver?where=m&sm=mtb_etc&mra=bjZF&qvt=0&query=CU%20%ED%96%89%EC%82%AC',
        'GS25': 'https://m.search.naver.com/search.naver?where=m&sm=mtb_etc&mra=bjZF&qvt=0&query=GS25%20%ED%96%89%EC%82%AC',
        '이마트24': 'https://m.search.naver.com/search.naver?where=m&sm=mtb_etc&mra=bjZF&qvt=0&query=%EC%9D%B4%EB%A7%88%ED%8A%B824%20%ED%96%89%EC%82%AC'
    }
    
    for brand, url in brand_urls.items():
        print(f"\n--- Checking {brand} ---")
        driver.get(url)
        time.sleep(3)
        
        tabs = driver.find_elements(By.CSS_SELECTOR, "ul.tab_list li a span")
        print(f"Tabs found: {[t.text for t in tabs]}")
        
        products = driver.find_elements(By.CSS_SELECTOR, "ul[role='list'] > li[role='listitem']")
        print(f"Products found: {len(products)}")
        if products:
            try:
                brand_info = products[0].find_element(By.CSS_SELECTOR, "span.store_info").text
                print(f"First product brand: {brand_info}")
            except:
                print("Could not find brand info for first product")

finally:
    driver.quit()
