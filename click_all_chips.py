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
    
    # 1. Find the brand filter dropdown or chips
    # Earlier I saw a select element with class 'slct'
    selects = driver.find_elements(By.CSS_SELECTOR, "select.slct")
    if selects:
        print(f"Found {len(selects)} select elements.")
        for i, s in enumerate(selects):
            options = s.find_elements(By.TAG_NAME, "option")
            print(f"Select {i} options: {[o.text for o in options]}")
            
    # 2. Find chips
    chips = driver.find_elements(By.CSS_SELECTOR, "a.fds-image-body-basic-chip-anchor")
    print(f"Found {len(chips)} chips.")
    for i, chip in enumerate(chips):
        print(f"Chip {i}: {chip.text}")

finally:
    driver.quit()
