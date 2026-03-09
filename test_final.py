from crawlers.all_crawler import crawl_all
import json

if __name__ == "__main__":
    print("--- Running Final Test Scraper ---")
    results = crawl_all()
    print(f"\nTotal products scraped: {len(results)}")
    
    brand_counts = {}
    for r in results:
        b = r['brand']
        brand_counts[b] = brand_counts.get(b, 0) + 1
        
    print("\n--- Scraped Brand Counts ---")
    for b, c in brand_counts.items():
        print(f"{b}: {c}")
        
    # Save a small sample to check
    with open('test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results[:20], f, ensure_ascii=False, indent=4)
