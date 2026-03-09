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
    # Try different queries
    queries = [
        '편의점 행사',
        'CU 편의점 행사',
        '이마트24 편의점 행사'
    ]
    
    for q in queries:
        print(f"\n--- Testing Query: {q} ---")
        url = f"https://m.search.naver.com/search.naver?where=m&query={q}"
        driver.get(url)
        time.sleep(5)
        
        # Check if the promotion table exists
        try:
            # Look for elements that indicate the promotion table
            tabs = driver.find_elements(By.CSS_SELECTOR, "ul.tab_list li a span")
            if tabs:
                print(f"Promotion table found! Tabs: {[t.text for t in tabs]}")
                products = driver.find_elements(By.CSS_SELECTOR, "ul[role='list'] > li[role='listitem']")
                if products:
                    brand = products[0].find_element(By.CSS_SELECTOR, "span.store_info").text
                    print(f"First product brand: {brand}")
            else:
                print("No tabs found.")
        except Exception as e:
            print(f"Error: {e}")

finally:
    driver.quit()
