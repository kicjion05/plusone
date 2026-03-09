from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

options = Options()
options.add_argument('--headless')
service = ChromeService()
driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get('https://cu.bgfretail.com/product/product.do?category=product&depth2=4&depth3=1')
    time.sleep(10)
    
    # 할인증정상품 클릭 시도
    clicked = driver.execute_script("""
        var links = document.querySelectorAll('a');
        for (var i = 0; i < links.length; i++) {
            if (links[i].innerText.includes('할인증정상품')) {
                links[i].click();
                return true;
            }
        }
        return false;
    """)
    print(f"Clicked filter: {clicked}")
    time.sleep(5)
    
    items = driver.find_elements(By.CSS_SELECTOR, 'li.prod_list')
    print(f"Total items found: {len(items)}")
    for i in range(min(10, len(items))):
        try:
            name = items[i].find_element(By.CSS_SELECTOR, "div.name p").text
            badge = items[i].find_element(By.CSS_SELECTOR, 'div.badge')
            print(f"--- Item {i}: {name} ---")
            print(badge.get_attribute('innerHTML'))
        except:
            pass
finally:
    driver.quit()
