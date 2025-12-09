import requests
import time
import csv
from typing import List, Dict, Set
import os

class YouTubeScraper:
    def __init__(self, api_key: str):
        self.API_KEY = api_key
        self.found_channels = set()

    def _make_api_request(self, url: str) -> Dict:
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Hatası: {e}")
            return {}

    def search_channels(self, search_term: str, max_results: int = 50) -> Set[str]:
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={search_term}&type=channel&maxResults={max_results}&key={self.API_KEY}"
        data = self._make_api_request(url)
        return {item['snippet']['channelId'] for item in data.get('items', [])}

    def get_channel_details(self, channel_ids: List[str]) -> List[Dict]:
        if not channel_ids:
            return []
        url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={','.join(channel_ids)}&key={self.API_KEY}"
        return self._make_api_request(url).get('items', [])

    def filter_channels(self, channels: List[Dict]) -> List[Dict]:
        valid_channels = []
        for channel in channels:
            stats = channel.get('statistics', {})
            snippet = channel.get('snippet', {})
            subs = int(stats.get('subscriberCount', 0))
            avg_views = int(stats.get('viewCount', 0)) / max(1, int(stats.get('videoCount', 1)))
            country = snippet.get('country', '').upper()

            if (100000 <= subs <= 700000 and 
                avg_views >= 50000 and 
                country in {'US', 'GB', 'CA', 'AU'}):
                
                valid_channels.append({
                    'Channel Name': snippet.get('title', ''),
                    'Subscriber Count': subs,
                    'Average Views': round(avg_views),
                    'Location': country,
                    'Channel Link': f"https://youtube.com/channel/{channel['id']}"
                })
        return valid_channels

    def scrape_by_terms(self, search_terms: List[str], max_results: int = 50, delay: float = 1.0) -> List[Dict]:
        all_channels = []
        for term in search_terms:
            print(f"Processing: {term}")
            channel_ids = self.search_channels(term, max_results)
            if not channel_ids:
                continue
            channels = self.get_channel_details(list(channel_ids))
            filtered = self.filter_channels(channels)
            all_channels.extend(filtered)
            time.sleep(delay)
        return all_channels

    def save_to_csv(self, data: List[Dict], filename: str = 'youtube_channels.csv'):
        if not data:
            print("No valid channels to save")
            return
    
        existing_rows = set()
        if os.path.exists(filename):
            with open(filename, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row_tuple = frozenset(row.items())  # Sıra bağımsız karşılaştırma
                    existing_rows.add(row_tuple)
    
        new_data = []
        for row in data:
            row_tuple = frozenset((str(k), str(v)) for k, v in row.items())  # Tip uyumu için str() ekledik
            if row_tuple not in existing_rows:
                new_data.append(row)
                existing_rows.add(row_tuple)
    
        if new_data:
            file_is_empty = not os.path.exists(filename) or os.path.getsize(filename) == 0
            with open(filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                if file_is_empty:
                    writer.writeheader()
                writer.writerows(new_data)
            print(f"Saved {len(new_data)} new channels to {filename}")
        else:
            print("No new unique channels to save")
