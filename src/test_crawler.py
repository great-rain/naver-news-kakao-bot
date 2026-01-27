"""
네이버 뉴스 크롤러 테스트 모듈
"""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from crawler import NaverNewsCrawler


class TestNaverNewsCrawler:
    """NaverNewsCrawler 테스트 클래스"""
    
    def test_init(self):
        """크롤러 초기화 테스트"""
        crawler = NaverNewsCrawler()
        assert crawler.base_url == "https://news.naver.com/main/list.naver"
        assert 'User-Agent' in crawler.headers
    
    @patch('crawler.requests.get')
    def test_get_breaking_news_success(self, mock_get):
        """뉴스 가져오기 성공 테스트"""
        # Mock HTML 응답 생성
        mock_html = """
        <html>
            <body>
                <ul class="type06_headline">
                    <li>
                        <dt><a href="/article/001/0012345678">테스트 뉴스 1</a></dt>
                    </li>
                    <li>
                        <dt><a href="/article/001/0012345679">테스트 뉴스 2</a></dt>
                    </li>
                </ul>
            </body>
        </html>
        """
        
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # 테스트 실행
        crawler = NaverNewsCrawler()
        news_list = crawler.get_breaking_news(limit=2)
        
        # 검증
        assert len(news_list) == 2
        assert news_list[0]['title'] == '테스트 뉴스 1'
        assert 'https://news.naver.com' in news_list[0]['url']
        mock_get.assert_called_once()
    
    @patch('crawler.requests.get')
    def test_get_breaking_news_network_error(self, mock_get):
        """네트워크 오류 테스트"""
        # 네트워크 오류 시뮬레이션 (requests.RequestException 사용)
        mock_get.side_effect = requests.RequestException("Connection error")
        
        crawler = NaverNewsCrawler()
        news_list = crawler.get_breaking_news()
        
        # 오류 발생 시 빈 리스트 반환
        assert news_list == []
    
    @patch('crawler.requests.get')
    def test_get_breaking_news_empty_result(self, mock_get):
        """뉴스가 없는 경우 테스트"""
        # 빈 HTML 응답
        mock_response = Mock()
        mock_response.text = "<html><body></body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        crawler = NaverNewsCrawler()
        news_list = crawler.get_breaking_news()
        
        assert news_list == []
    
    def test_format_news_message(self):
        """메시지 포맷팅 테스트"""
        crawler = NaverNewsCrawler()
        
        news_list = [
            {'title': '뉴스 1', 'url': 'https://news.naver.com/article/1'},
            {'title': '뉴스 2', 'url': 'https://news.naver.com/article/2'}
        ]
        
        message = crawler.format_news_message(news_list)
        
        assert '오늘의 네이버 뉴스 TOP 10' in message
        assert '뉴스 1' in message
        assert '뉴스 2' in message
        assert 'https://news.naver.com/article/1' in message
    
    def test_format_news_message_empty(self):
        """빈 뉴스 리스트 포맷팅 테스트"""
        crawler = NaverNewsCrawler()
        message = crawler.format_news_message([])
        
        assert message == "오늘의 뉴스를 가져올 수 없습니다."


@pytest.mark.integration
class TestNaverNewsCrawlerIntegration:
    """통합 테스트 (실제 네트워크 요청)"""
    
    def test_get_breaking_news_real(self):
        """실제 네이버 뉴스 페이지 크롤링 테스트"""
        crawler = NaverNewsCrawler()
        news_list = crawler.get_breaking_news(limit=5)
        
        # 실제로 뉴스를 가져왔는지 확인
        assert len(news_list) > 0
        assert all('title' in news for news in news_list)
        assert all('url' in news for news in news_list)
        assert all(news['url'].startswith('http') for news in news_list)
    
    def test_format_news_message_real(self):
        """실제 뉴스로 메시지 포맷팅 테스트"""
        crawler = NaverNewsCrawler()
        news_list = crawler.get_breaking_news(limit=3)
        
        if news_list:
            message = crawler.format_news_message(news_list)
            assert len(message) > 0
            assert '오늘의 네이버 뉴스 TOP 10' in message
