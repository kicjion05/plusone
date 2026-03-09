from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
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
    
    print('--- Selecting 음료 Tab ---')
    tab = driver.find_element(By.XPATH, "//ul[contains(@class, 'tab_list')]//a[span[text()='음료']]")
    driver.execute_script("arguments[0].click();", tab)
    time.sleep(2)
    
    print('--- Selecting 이마트24 Brand ---')
    select_el = driver.find_element(By.CSS_SELECTOR, "select.slct")
    select_obj = Select(select_el)
    for opt in select_obj.options:
        if '24' in opt.text:
            select_obj.select_by_value(opt.get_attribute('value'))
            break
    time.sleep(3)
    
    # Check if 음료 tab is still selected
    tab_parent = driver.find_element(By.XPATH, "//ul[contains(@class, 'tab_list')]//li[a/span[text()='음료']]")
    is_selected = tab_parent.get_attribute('aria-selected')
    print(f"음료 tab selected: {is_selected}")

finally:
    driver.quit()
