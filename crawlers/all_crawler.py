import time
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

def crawl_all():
    print("WebDriver를 설정합니다...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("window-size=1920x1080")
    options.add_argument("user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604.1")
    
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    products_data = []
    processed_products = set()

    try:
        base_url = "https://m.search.naver.com/search.naver?where=m&sm=mtb_etc&mra=bjZF&qvt=0&query=%ED%8E%B8%EC%9D%98%EC%A0%90%ED%96%89%EC%82%AC"
        # 사용자가 확인한 실제 탭 명칭 반영
        main_categories = ["음료", "아이스크림", "과자", "간편식사", "생활용품"]
        brands = ["GS25", "CU", "세븐일레븐", "이마트24"]

        
        for brand_name in brands:
            print(f"\n>>> 브랜드 '{brand_name}' 크롤링 시작")
            
            for main_cat_name in main_categories:
                # 매번 베이스 페이지로 이동 (상태 초기화)
                driver.get(base_url)
                time.sleep(2)
                
                # 1. 브랜드 선택
                found_brand = False
                try:
                    select_el = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "select.slct")))
                    select_obj = Select(select_el)
                    for opt in select_obj.options:
                        if brand_name.lower() in opt.text.lower():
                            select_obj.select_by_value(opt.get_attribute('value'))
                            found_brand = True
                            break
                    if not found_brand:
                        chips = driver.find_elements(By.CSS_SELECTOR, "a.fds-image-body-basic-chip-anchor")
                        for chip in chips:
                            if brand_name.lower() in chip.text.lower() or (brand_name == "이마트24" and "24" in chip.text):
                                driver.execute_script("arguments[0].click();", chip)
                                found_brand = True
                                break
                except: pass
                
                if not found_brand:
                    print(f"  - '{brand_name}' 필터를 찾을 수 없어 건너뜁니다.")
                    break # 이 브랜드는 지원되지 않는 것으로 판단

                time.sleep(2)

                # 2. 카테고리 탭 선택 (CU처럼 탭이 없을 경우 대비)
                has_tabs = False
                try:
                    tab_xpath = "//ul[contains(@class, 'tab_list')]//a[span[contains(text(), '{}')]]".format(main_cat_name[:2])
                    main_tab_link = driver.find_element(By.XPATH, tab_xpath)
                    if main_tab_link.is_displayed():
                        driver.execute_script("arguments[0].click();", main_tab_link)
                        time.sleep(1)
                        has_tabs = True
                        print(f"  - '{main_cat_name}' 탭 활성화 성공")
                except:
                    if main_cat_name == main_categories[0]:
                        print(f"  - '{brand_name}'은 카테고리 탭이 없습니다. 전체 리스트를 수집합니다.")
                    else:
                        # 첫 카테고리가 아니면 이미 '전체'에서 다 긁었을 가능성이 큼
                        print(f"  - '{main_cat_name}' 탭이 없어 건너뜁니다.")
                        continue

                # 3. 데이터 수집
                page_num = 1
                while True:
                    try:
                        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul[role='list'] > li[role='listitem']")))
                        products = driver.find_elements(By.CSS_SELECTOR, "ul[role='list'] > li[role='listitem']")
                    except: break

                    new_items_in_page = 0
                    for product in products:
                        try:
                            name = product.find_element(By.CSS_SELECTOR, "strong.item_name span.name_text").text
                            try:
                                s_brand = product.find_element(By.CSS_SELECTOR, "span.store_info").text
                                if not s_brand: s_brand = brand_name
                            except: s_brand = brand_name
                            
                            if (name, s_brand) in processed_products: continue
                            
                            img = product.find_element(By.CSS_SELECTOR, "a.thumb img").get_attribute('src')
                            event = "N/A"
                            try: event = product.find_element(By.CSS_SELECTOR, "strong.item_name span.ico_event").text
                            except: pass
                            
                            # 가격 정보 추출
                            sale_price, original_price = 0, 0
                            try:
                                sale_price_str = product.find_element(By.CSS_SELECTOR, "p.item_price em").text.replace(',', '').replace('원', '').strip()
                                sale_price = int(sale_price_str)
                                
                                try:
                                    # 할인 전 가격(정가)이 별도로 표시된 경우
                                    original_price_str = product.find_element(By.CSS_SELECTOR, "p.item_price span.item_discount").text.replace(',', '').replace('원', '').strip()
                                    original_price = int(original_price_str)
                                except:
                                    # 정가 정보가 없으면 판매가와 동일하게 설정 (DB NOT NULL 제약 대응)
                                    original_price = sale_price
                            except:
                                pass

                            products_data.append({
                                "brand": s_brand, 
                                "name": name, 
                                "sale_price": sale_price, 
                                "original_price": original_price,
                                "image_url": img, 
                                "category": main_cat_name, 
                                "event_type": event
                            })
                            processed_products.add((name, s_brand))
                            new_items_in_page += 1
                        except: continue
                    
                    if new_items_in_page == 0 and page_num > 1: break
                    
                    # 다음 페이지
                    try:
                        current_page_text = driver.find_element(By.CSS_SELECTOR, "strong.cmm_npgs_now._current").text
                        next_btn = driver.find_element(By.CSS_SELECTOR, "a.cmm_pg_next.on")
                        driver.execute_script("arguments[0].click();", next_btn)
                        WebDriverWait(driver, 5).until(wait_for_page_number_to_change((By.CSS_SELECTOR, "strong.cmm_npgs_now._current"), current_page_text))
                        page_num += 1
                    except: break
                
                # 탭이 없는 브랜드는 '전체' 카테고리 하나에서 모든 데이터를 가져온 것으로 간주하고 브랜드 루프 종료
                if not has_tabs:
                    break

    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        driver.quit()
    return products_data
