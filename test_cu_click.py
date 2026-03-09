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
    
    print('--- Looking for Brand Chips ---')
    # Let's find all chips
    chips = driver.find_elements(By.CSS_SELECTOR, "a.fds-image-body-basic-chip-anchor")
    cu_chip = None
    for chip in chips:
        if 'CU' in chip.text.upper():
            cu_chip = chip
            print(f"Found CU Chip: {chip.text}")
            break
    
    if cu_chip:
        print("Clicking CU Chip...")
        driver.execute_script("arguments[0].click();", cu_chip)
        time.sleep(3)
        
        print('--- Scraping Products After Clicking CU ---')
        products = driver.find_elements(By.CSS_SELECTOR, "ul[role='list'] > li[role='listitem']")
        print(f"Found {len(products)} items.")
        for i, product in enumerate(products):
            try:
                name = product.find_element(By.CSS_SELECTOR, "strong.item_name span.name_text").text
                brand = product.find_element(By.CSS_SELECTOR, "span.store_info").text
                print(f"Item {i}: [{brand}] {name}")
            except:
                pass
    else:
        print("CU Chip not found. Let's dump all chip texts.")
        for chip in chips:
            print(f"Chip: {chip.text}")

finally:
    driver.quit()
