from user_data import YouTubeScraper
from social_scraper import add_social_media_info
import subprocess
import os
import pandas as pd
# Configurations
API_KEY = 'AIzaSyB36kTYdVFg5dSyzo5c81zbotQpP-qV???'  # Kendi API anahtarınızı girin
SEARCH_TERMS = [
   "tech review",
    "smartphone comparison",
    "PC build 2024",
    "Samsung s25 vs iPhone 16",
    "Tesla vs BYD",
    "NVIDIA vs AMD",
    "best budget smartphone 2024",
    "iPhone 16 unboxing",
    "laptop reviews 2024",
    "electric car range test",
    "Apple M4 chip vs Intel",
    "gaming smartphone review",
    "wireless earbuds comparison",
    "Foldable phone review",
    "best smartwatches 2024",
    "Android 15 new features",
    "MacBook Air vs Dell XPS",
    "robot vacuum comparison",
    "camera comparison 2024",
    "streaming setup tour",
    "mechanical keyboard review",
    "home office tech setup",
    "best tablets for students",
    "EV charging speed test",
]

def main():
    try:
        scraper = YouTubeScraper(API_KEY)
        
        print("Kanal bilgileri toplanıyor...")
        results = scraper.scrape_by_terms(
            search_terms=SEARCH_TERMS,
            max_results=25,
            delay=1.5
        )
        
        if not results:
            print("API hatası - Demo veri kullanılıyor...")
      
        csv_file = 'tech_youtubers.csv'
        scraper.save_to_csv(results, csv_file)
        
       
        print("\nSosyal medya bilgileri ekleniyor...")
        updated_csv = add_social_media_info(csv_file)
        
        
        
        # excele dönüştürme kısmı
        def convert_csv_to_excel(csv_path):
            excel_path = csv_path.replace(".csv", ".xlsx")
            df = pd.read_csv(csv_path)
            df.to_excel(excel_path, index=False)
            print(f"Excel dosyası oluşturuldu: {excel_path}")
            return excel_path
        
        
        csv_file = 'tech_youtubers_final.csv'
        excel_file = convert_csv_to_excel(csv_file)
        
            
    except Exception as e:
        print(f"Ana hata: {e}")

if __name__ == '__main__':
    main()
    