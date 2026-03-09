from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    # 2번(과자류) 카테고리에서 아이스크림으로 오인될만한 것들 확인
    url = 'https://emart24.co.kr/goods/event?search=&category_seq=&base_category_seq=2&align='
    driver.get(url)
    time.sleep(10)
    
    items = driver.execute_script("""
        let res = [];
        document.querySelectorAll('.itemWrap').forEach(item => {
            let name = item.querySelector('.itemtitle p a').innerText.trim();
            res.push(name);
        });
        return res;
    """)
    
    print("--- '과자' 카테고리 내 상품 샘플 ---")
    for name in items:
        # 기존 로직에서 아이스크림으로 분류될만한 키워드들
        if any(x in name for x in ["바", "콘", "아이스"]):
            print(f"체크 필요: {name}")
            
finally:
    driver.quit()
