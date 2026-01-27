"""
메인 실행 파일
네이버 뉴스를 크롤링하고 카카오톡으로 전송합니다.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from crawler import NaverNewsCrawler
from kakao_sender import KakaoSender

# .env 파일 로드 (프로젝트 루트 기준)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


def main():
    """메인 함수"""
    print("=" * 50)
    print("📰 네이버 뉴스 카카오톡 자동 발송 봇")
    print(f"⏰ 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 환경 변수 로드
    client_id = os.getenv('KAKAO_CLIENT_ID')
    refresh_token = os.getenv('KAKAO_REFRESH_TOKEN')
    client_secret = os.getenv('KAKAO_CLIENT_SECRET')
    
    if not client_id or not refresh_token:
        print("❌ 오류: 환경 변수가 설정되지 않았습니다.")
        print("   KAKAO_CLIENT_ID와 KAKAO_REFRESH_TOKEN을 설정해주세요.")
        sys.exit(1)
    
    # 1. 네이버 뉴스 크롤링
    print("\n🔍 네이버 뉴스 크롤링 시작...")
    crawler = NaverNewsCrawler()
    news_list = crawler.get_breaking_news(limit=10)
    
    if not news_list:
        print("❌ 뉴스를 가져오지 못했습니다.")
        sys.exit(1)
    
    print(f"✅ {len(news_list)}개의 뉴스를 수집했습니다.")
    
    # 2. 메시지 포맷팅
    message = crawler.format_news_message(news_list)
    
    # 3. 카카오톡 전송
    print("\n📱 카카오톡 메시지 전송 시작...")
    sender = KakaoSender(client_id, refresh_token, client_secret)
    
    if sender.send_message(message):
        print("\n" + "=" * 50)
        print("🎉 모든 작업이 성공적으로 완료되었습니다!")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ 메시지 전송에 실패했습니다.")
        print("=" * 50)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)