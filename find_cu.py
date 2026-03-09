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
    
    print('--- Searching for "CU" ---')
    elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'CU')]")
    for el in elements:
        try:
            txt = el.text
            if el.is_displayed() and 'CU' in txt:
                print(f"Tag: {el.tag_name}, Class: {el.get_attribute('class')}, Text: {txt[:50]}")
        except:
            pass

    # Specifically look for the filter section
    print('\n--- Filter Sections ---')
    filters = driver.find_elements(By.CSS_SELECTOR, "div[class*='filter'], ul[class*='tab'], div[class*='chip']")
    for f in filters:
        try:
            txt = f.text
            if f.is_displayed() and txt:
                print(f"Filter Candidate: Tag={f.tag_name}, Class={f.get_attribute('class')}, Text={txt[:100]}")
        except:
            pass

finally:
    driver.quit()
