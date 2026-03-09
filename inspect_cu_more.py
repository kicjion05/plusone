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
    
    # 할인증정상품 클릭
    driver.execute_script("""
        var links = document.querySelectorAll('a');
        for (var i = 0; i < links.length; i++) {
            if (links[i].innerText.includes('할인증정상품')) {
                links[i].click();
                break;
            }
        }
    """)
    time.sleep(5)
    
    for i in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        try:
            more_btn = driver.find_element(By.CSS_SELECTOR, "div.prodListBtn-nav a")
            print(f"[{i}] Clicking more...")
            driver.execute_script("arguments[0].click();", more_btn)
            time.sleep(3)
        except:
            print(f"[{i}] More button not found.")
            break
            
    try:
        nav = driver.find_element(By.CSS_SELECTOR, "div.prodListBtn-nav")
        print("Final Nav Text:", nav.text.strip())
    except:
        print("Nav area not found.")

finally:
    driver.quit()
