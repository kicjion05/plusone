import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class wait_for_page_number_to_change:
    def __init__(self, locator, old_text):
        self.locator = locator
        self.old_text = old_text
    def __call__(self, driver):
        try:
            new_text = driver.find_element(*self.locator).text
            return new_text != self.old_text
        except (StaleElementReferenceException, NoSuchElementException):
            return False

def safe_get(driver, url, retries=3):
    """네트워크 에러에 대응하기 위한 재시도 로직"""
    for i in range(retries):
        try:
            driver.get(url)
            return True
        except WebDriverException as e:
            print(f"      ! 페이지 로드 실패 (시도 {i+1}/{retries}): {e}")
            time.sleep(3)
    return False

def crawl_cu_official(driver, processed_products):
    print("\n  -- [백업] CU 공식 홈페이지 크롤링 시작")
    cu_products = []
    
    # 1:간편식사, 2:즉석조리, 3:과자류, 4:아이스크림, 5:식품, 6:음료, 7:생활용품
    categories = [
        {"id": "1", "name": "간편식사"},
        {"id": "2", "name": "즉석조리"},
        {"id": "3", "name": "과자"},
        {"id": "4", "name": "아이스크림"},
        {"id": "5", "name": "식품"},
        {"id": "6", "name": "음료"},
        {"id": "7", "name": "생활용품"}
    ]

    for cat in categories:
        url = f"https://cu.bgfretail.com/product/product.do?category=product&depth2=4&depth3={cat['id']}"
        if not safe_get(driver, url): continue
        time.sleep(5)
        
        try:
            # '할인증정상품' 필터 적용 (텍스트 매칭 + JS 호출)
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
            
            # 더보기 버튼 끝까지 클릭 (nextPage 함수 직접 호출 방식)
            print(f"      * 전체 상품 로딩 중 (nextPage 호출)...")
            page_idx = 1
            while True:
                try:
                    # 현재 상품 수 기록
                    before_count = driver.execute_script("return document.querySelectorAll('li.prod_list').length;")
                    
                    # nextPage(idx) 호출
                    print(f"        - {page_idx}번 더보기 호출 중...", end="\r")
                    driver.execute_script(f"nextPage({page_idx});")
                    time.sleep(3) # 데이터 로딩 대기
                    
                    # 호출 후 상품 수 확인
                    after_count = driver.execute_script("return document.querySelectorAll('li.prod_list').length;")
                    
                    # 상품 수가 늘지 않았거나 '조회된 상품이 없습니다' 확인
                    if after_count <= before_count:
                        # 한 번 더 확인 (로딩이 느릴 수 있음)
                        time.sleep(2)
                        after_count = driver.execute_script("return document.querySelectorAll('li.prod_list').length;")
                        if after_count <= before_count:
                            break
                    
                    # '조회된 상품이 없습니다' 문구가 보이면 종료
                    is_end = driver.execute_script("""
                        var nav = document.querySelector('div.prodListBtn-nav');
                        if (!nav) return false;
                        return nav.innerText.includes('없습니다');
                    """)
                    if is_end: break
                    
                    page_idx += 1
                    if page_idx > 50: break # 무한루프 방지
                except:
                    break
            print(f"\n      * 로딩 완료 (최종 {page_idx}페이지 분량 로드)")

            # 데이터 추출 (배지 정보 추출 로직 강화)
            items_raw = driver.execute_script("""
                var results = [];
                document.querySelectorAll('li.prod_list').forEach(function(item) {
                    var name = item.querySelector('div.name p') ? item.querySelector('div.name p').innerText : '';
                    var img_el = item.querySelector('div.prod_img img');
                    var img = img_el ? (img_el.src || img_el.getAttribute('data-src')) : '';
                    var price = item.querySelector('div.price strong') ? item.querySelector('div.price strong').innerText : '0';
                    
                    // 배지 정보: alt 속성 혹은 클래스명에서 추출
                    var badge_el = item.querySelector('div.badge span');
                    var badge_text = badge_el ? (badge_el.innerText || badge_el.className) : '';
                    var badge_img = item.querySelector('div.badge img');
                    if (badge_img) badge_text += " " + badge_img.alt;
                    
                    results.push({ name: name, img: img, price: price, badge: badge_text });
                });
                return results;
            """)

            for raw in items_raw:
                if not raw['name'] or (raw['name'], "CU") in processed_products: continue
                
                # 1+1, 2+1 등 행사 유형 판별
                b_txt = raw['badge'].lower()
                event_type = "할인"
                if '1plus1' in b_txt or '1+1' in b_txt or 'plus1' in b_txt: event_type = "1+1"
                elif '2plus1' in b_txt or '2+1' in b_txt or 'plus2' in b_txt: event_type = "2+1"
                elif '3plus1' in b_txt or '3+1' in b_txt: event_type = "3+1"
                
                img_url = raw['img']
                if img_url.startswith('//'): img_url = 'https:' + img_url
                
                try: sale_p = int(raw['price'].replace(',', '').replace('원', '').strip())
                except: sale_p = 0

                cu_products.append({
                    "brand": "CU", "name": raw['name'], "sale_price": sale_p, "original_price": sale_p,
                    "image_url": img_url, "category": cat['name'], "event_type": event_type
                })
                processed_products.add((raw['name'], "CU"))
            
            print(f"    - CU '{cat['name']}' 완료 (총 {len(cu_products)}개)")
        except Exception as e:
            print(f"    ! CU '{cat['name']}' 처리 중 오류: {e}")
            
    return cu_products

def crawl_emart24_official(driver, processed_products):
    print("\n  -- [직접] 이마트24 공식 홈페이지 크롤링 시작")
    emart_products = []
    
    # 이마트24 공식 카테고리 (1:간편식사, 2:과자, 3:생활용품, 5:음료)
    # 아이스크림은 '과자' 분류 내에서 정밀 추출
    categories = [
        {"id": "1", "name": "간편식사"},
        {"id": "2", "name": "과자"},
        {"id": "3", "name": "생활용품"},
        {"id": "5", "name": "음료"},
        {"id": "", "name": "기타"}
    ]

    for cat in categories:
        page = 1
        print(f"    * 이마트24 '{cat['name'] or '전체'}' 수집 중...", end="")
        cat_count = 0
        while True:
            try:
                url = f"https://emart24.co.kr/goods/event?search=&category_seq=&base_category_seq={cat['id']}&align=&page={page}"
                if not safe_get(driver, url): break
                
                # 페이지 로딩 대기
                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "itemWrap")))
                except:
                    break # 상품 없음
                
                items_raw = driver.execute_script("""
                    let results = [];
                    document.querySelectorAll('.itemWrap').forEach(function(item) {
                        let name = "";
                        let name_el = item.querySelector('.itemtitle p a');
                        if (name_el) name = name_el.innerText.trim();
                        
                        let img = "";
                        let img_el = item.querySelector('.itemTit img') || item.querySelector('.itemImg img') || item.querySelector('img');
                        if (img_el) img = img_el.src;
                        
                        let event = "";
                        if (item.querySelector('.onepl')) event = "1+1";
                        else if (item.querySelector('.twopl')) event = "2+1";
                        else if (item.querySelector('.tripl')) event = "3+1";
                        else if (item.querySelector('.sale')) event = "할인";
                        
                        if (!event || event.includes('골라') || event.includes('gola')) return;
                        
                        let sale_p = "0";
                        let sale_p_el = item.querySelector('.price');
                        if (sale_p_el) sale_p = sale_p_el.innerText.trim();
                        
                        let orig_p = sale_p;
                        let orig_p_el = item.querySelector('.priceOff');
                        if (orig_p_el) orig_p = orig_p_el.innerText.trim();
                        
                        results.push({ name: name, img: img, event: event, sale_price: sale_p, original_price: orig_p });
                    });
                    return results;
                """)
                
                if not items_raw: break
                
                new_in_page = 0
                for raw in items_raw:
                    if not raw['name'] or (raw['name'], "이마트24") in processed_products: continue
                    
                    try: sale_p = int(raw['sale_price'].replace(',', '').replace('원', '').strip())
                    except: sale_p = 0
                    try: orig_p = int(raw['original_price'].replace(',', '').replace('원', '').strip())
                    except: orig_p = sale_p
                    
                    # 사이트 공식 카테고리 이름을 그대로 사용 (보정 로직 제거)
                    cat_name = cat['name'] or "기타"

                    emart_products.append({
                        "brand": "이마트24", "name": raw['name'], "sale_price": sale_p, "original_price": orig_p,
                        "image_url": raw['img'], "category": cat_name, "event_type": raw['event']
                    })
                    processed_products.add((raw['name'], "이마트24"))
                    new_in_page += 1
                    cat_count += 1
                
                if new_in_page == 0: break 
                page += 1
                if page > 100: break
                time.sleep(1)
                
            except Exception as e:
                print(f"\n    ! 오류 발생: {e}")
                if "session" in str(e).lower(): return emart_products
                break
        print(f" 완료 ({cat_count}개)")
            
    return emart_products

def crawl_all():
    print("WebDriver 설정 중...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("window-size=1920x1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    products_data = []
    processed_products = set()

    try:
        base_url = "https://m.search.naver.com/search.naver?where=m&sm=mtb_etc&mra=bjZF&qvt=0&query=%ED%8E%B8%EC%9D%98%EC%A0%90%ED%96%89%EC%82%AC"
        main_categories = ["음료", "아이스크림", "과자", "간편식사", "생활용품"]
        brands = ["이마트24", "GS25", "CU", "세븐일레븐"]
        
        for brand_name in brands:
            print(f"\n>>> 브랜드 '{brand_name}' 크롤링 시작")
            
            # 브랜드가 바뀔 때마다 세션을 깨끗하게 유지하기 위해 페이지 새로고침
            if not safe_get(driver, base_url): continue
            time.sleep(5) # 네이버 스마트블록 로딩 대기

            if brand_name == "이마트24":
                products_data.extend(crawl_emart24_official(driver, processed_products))
                continue
            
            brand_found_in_naver = False
            if brand_name != "CU":
                # 브랜드 필터 적용 (한 번만 확실하게)
                if not safe_get(driver, base_url): continue
                time.sleep(5)
                
                try:
                    found_f = False
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "select.slct, a.fds-image-body-basic-chip-anchor")))
                    select_elements = driver.find_elements(By.CSS_SELECTOR, "select.slct")
                    if select_elements:
                        select_obj = Select(select_elements[0])
                        for opt in select_obj.options:
                            if brand_name.lower() in opt.text.lower():
                                select_obj.select_by_value(opt.get_attribute('value'))
                                found_f = True; break
                    if not found_f:
                        chips = driver.find_elements(By.CSS_SELECTOR, "a.fds-image-body-basic-chip-anchor")
                        for chip in chips:
                            if brand_name.lower() in chip.text.lower() or (brand_name == "이마트24" and "24" in chip.text):
                                driver.execute_script("arguments[0].click();", chip)
                                found_f = True; break
                    if not found_f: continue
                    time.sleep(3)
                except Exception as e:
                    print(f"    ! '{brand_name}' 필터 선택 실패: {e}")
                    continue

                # 각 카테고리 순회
                for main_cat_name in main_categories:
                    try:
                        # 카테고리 탭 클릭
                        tab_xpath = f"//ul[contains(@class, 'tab_list')]//a[span[contains(text(), '{main_cat_name[:2]}')]]"
                        tab_el = WebDriverWait(driver, 7).until(EC.element_to_be_clickable((By.XPATH, tab_xpath)))
                        driver.execute_script("arguments[0].click();", tab_el)
                        time.sleep(3)
                        brand_found_in_naver = True
                        
                        # 해당 카테고리 끝까지 페이징하며 수집
                        while True:
                            try:
                                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul[role='list'] > li[role='listitem']")))
                                products = driver.find_elements(By.CSS_SELECTOR, "ul[role='list'] > li[role='listitem']")
                            except: break

                            new_count = 0
                            for product in products:
                                try:
                                    name = product.find_element(By.CSS_SELECTOR, "strong.item_name span.name_text").text.strip()
                                    try: s_brand = product.find_element(By.CSS_SELECTOR, "span.store_info").text or brand_name
                                    except: s_brand = brand_name
                                    
                                    if (name, s_brand) in processed_products: continue
                                    
                                    img = product.find_element(By.CSS_SELECTOR, "a.thumb img").get_attribute('src')
                                    event = "할인"
                                    try: event = product.find_element(By.CSS_SELECTOR, "strong.item_name span.ico_event").text
                                    except: pass
                                    
                                    sale_p, orig_p = 0, 0
                                    try:
                                        sale_p = int(product.find_element(By.CSS_SELECTOR, "p.item_price em").text.replace(',', '').replace('원', '').strip())
                                        try: orig_p = int(product.find_element(By.CSS_SELECTOR, "p.item_price span.item_discount").text.replace(',', '').replace('원', '').strip())
                                        except: orig_p = sale_p
                                    except: pass

                                    products_data.append({"brand": s_brand, "name": name, "sale_price": sale_p, "original_price": orig_p, "image_url": img, "category": main_cat_name, "event_type": event})
                                    processed_products.add((name, s_brand))
                                    new_count += 1
                                except: continue
                            
                            # 다음 페이지 버튼 확인 및 클릭
                            try:
                                next_btn = driver.find_element(By.CSS_SELECTOR, "a.cmm_pg_next.on")
                                curr_txt = driver.find_element(By.CSS_SELECTOR, "strong.cmm_npgs_now._current").text
                                driver.execute_script("arguments[0].click();", next_btn)
                                WebDriverWait(driver, 10).until(wait_for_page_number_to_change((By.CSS_SELECTOR, "strong.cmm_npgs_now._current"), curr_txt))
                            except:
                                break # 다음 버튼이 없거나 비활성화 상태면 종료
                                
                    except Exception as e:
                        print(f"    ! '{main_cat_name}' 수집 중 오류: {e}")
                        continue

            if brand_name == "CU" and not brand_found_in_naver:
                products_data.extend(crawl_cu_official(driver, processed_products))

    except Exception as e:
        print(f"전체 공정 오류: {e}")
    finally:
        driver.quit()
    return products_data
