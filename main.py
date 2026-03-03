import json
import os
import sys
import io
from dotenv import load_dotenv
from supabase import create_client, Client
from crawlers.all_crawler import crawl_all

# 윈도우 터미널 한글 깨짐 방지 (가장 안전한 방식)
if sys.platform == 'win32':
    try:
        # Python 3.7+ 에서 권장되는 방식
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # 하위 버전 대응
        import locale
        if locale.getpreferredencoding().upper() != 'UTF-8':
            os.environ['PYTHONIOENCODING'] = 'UTF-8'

def main():
    """
    통합 크롤러를 실행하여 모든 편의점의 행사 상품을 수집하고,
    결과를 JSON 파일 및 Supabase 데이터베이스에 저장합니다.
    """
    print(">>> 프로그램이 정상적으로 시작되었습니다. 잠시만 기다려주세요...")
    
    try:
        print(">>> 통합 편의점 행사 상품 크롤링을 시작합니다.")
        
        # 크롤링 실행
        all_products = crawl_all()
        
        if not all_products:
            print("\n>>> 수집된 상품이 없습니다. 크롤러 설정을 확인하세요.")
            return

        # 1. JSON 파일로 저장
        with open('all_products.json', 'w', encoding='utf-8') as f:
            json.dump(all_products, f, ensure_ascii=False, indent=4)
        print(f"\n>>> 파일 저장 완료. 총 {len(all_products)}개의 상품 정보를 'all_products.json'에 저장했습니다.")

        # 2. Supabase에 데이터 삽입
        load_dotenv()
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            print("\n>>> 경고: Supabase 환경 변수가 설정되지 않아 DB 업로드를 건너뜁니다.")
        else:
            try:
                supabase: Client = create_client(supabase_url, supabase_key)
                print("\n>>> Supabase에 데이터 삽입을 시작합니다...")
                
                print(">>> 기존 데이터를 삭제 중...")
                supabase.table('products').delete().neq('id', -1).execute()

                print(">>> 새로운 데이터를 삽입 중...")
                response = supabase.table('products').insert(all_products).execute()
                
                if response.data:
                    print(f">>> Supabase에 총 {len(response.data)}개의 데이터가 성공적으로 삽입되었습니다.")
            except Exception as e:
                print(f">>> Supabase 작업 중 오류 발생: {e}")

    except Exception as e:
        print(f"\n[치명적 오류 발생] {e}")
        import traceback
        traceback.print_exc()

    print("\n>>> 모든 작업이 종료되었습니다.")

if __name__ == "__main__":
    main()
