"""
네이버 뉴스 크롤링 모듈
네이버 뉴스 속보 페이지에서 상위 10개 기사를 추출합니다.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict


class NaverNewsCrawler:
    """네이버 뉴스 크롤러 클래스"""
    
    def __init__(self):
        self.base_url = "https://news.naver.com/main/list.naver"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_breaking_news(self, limit: int = 10) -> List[Dict[str, str]]:
        """
        네이버 속보 뉴스 가져오기
        
        Args:
            limit: 가져올 뉴스 개수 (기본값: 10)
        
        Returns:
            뉴스 리스트 (제목, URL 포함)
        """
        params = {
            'mode': 'LSD',
            'mid': 'sec',
            'sid1': '001'  # 정치
        }
        
        try:
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_list = []
            
            # 뉴스 리스트 추출
            news_items = soup.select('ul.type06_headline li') + soup.select('ul.type06 li')
            
            for item in news_items[:limit]:
                link_tag = item.select_one('dt:not(.photo) a') or item.select_one('a')
                if link_tag:
                    title = link_tag.get_text(strip=True)
                    url = link_tag.get('href', '')
                    
                    # URL이 상대경로인 경우 절대경로로 변환
                    if url.startswith('/'):
                        url = 'https://news.naver.com' + url
                    
                    news_list.append({
                        'title': title,
                        'url': url
                    })
                
                if len(news_list) >= limit:
                    break
            
            return news_list
        
        except requests.RequestException as e:
            print(f"크롤링 중 오류 발생: {e}")
            return []
    
    def format_news_message(self, news_list: List[Dict[str, str]]) -> str:
        """
        뉴스 리스트를 메시지 형식으로 포맷팅
        
        Args:
            news_list: 뉴스 리스트
        
        Returns:
            포맷팅된 메시지 문자열
        """
        if not news_list:
            return "오늘의 뉴스를 가져올 수 없습니다."
        
        message = "📰 오늘의 네이버 뉴스 TOP 10\n\n"
        
        for idx, news in enumerate(news_list, 1):
            message += f"{idx}. {news['title']}\n"
            message += f"   🔗 {news['url']}\n\n"
        
        return message.strip()


if __name__ == "__main__":
    # 테스트 코드
    crawler = NaverNewsCrawler()
    news = crawler.get_breaking_news(10)
    
    if news:
        print(f"✅ {len(news)}개의 뉴스를 가져왔습니다.\n")
        print(crawler.format_news_message(news))
    else:
        print("❌ 뉴스를 가져오지 못했습니다.")