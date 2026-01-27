"""
카카오톡 메시지 전송 모듈
카카오 API를 사용하여 '나에게 보내기' 기능을 구현합니다.
"""

import requests
import json
from typing import Optional


class KakaoSender:
    """카카오톡 메시지 전송 클래스"""
    
    def __init__(self, client_id: str, refresh_token: str, client_secret: str = None):
        """
        Args:
            client_id: 카카오 REST API 키
            refresh_token: 카카오 Refresh Token
            client_secret: 카카오 Client Secret (선택)
        """
        self.client_id = client_id
        self.refresh_token = refresh_token
        self.client_secret = client_secret  # 이 줄 추가
        self.access_token = None
        self.token_url = "https://kauth.kakao.com/oauth/token"
        self.message_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    
    def get_access_token(self) -> bool:
        """
        Refresh Token을 사용하여 새로운 Access Token 발급
        
        Returns:
            성공 여부
        """
        data = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'refresh_token': self.refresh_token
        }
        
        if self.client_secret:
            data['client_secret'] = self.client_secret

        try:
            response = requests.post(self.token_url, data=data)
            
            # 에러 상세 정보 출력
            if response.status_code != 200:
                print(f"\n🔍 에러 상세 정보:")
                print(f"   Status Code: {response.status_code}")
                print(f"   응답 내용: {response.text}")
                try:
                    error_info = response.json()
                    print(f"   에러 코드: {error_info.get('error', 'Unknown')}")
                    print(f"   에러 설명: {error_info.get('error_description', 'No description')}")
                except:
                    pass
            
            response.raise_for_status()
            
            tokens = response.json()
            self.access_token = tokens.get('access_token')
            
            # Refresh Token이 갱신된 경우 업데이트
            new_refresh_token = tokens.get('refresh_token')
            if new_refresh_token:
                self.refresh_token = new_refresh_token
                print(f"⚠️ Refresh Token이 갱신되었습니다: {new_refresh_token}")
            
            print("✅ Access Token 발급 성공")
            return True
        
        except requests.RequestException as e:
            print(f"❌ Access Token 발급 실패: {e}")
            return False
    
    def send_message(self, message: str) -> bool:
        """
        카카오톡 '나에게 보내기'로 메시지 전송
        
        Args:
            message: 전송할 메시지
        
        Returns:
            성공 여부
        """
        if not self.access_token:
            if not self.get_access_token():
                return False
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # 텍스트 템플릿 생성
        template = {
            "object_type": "text",
            "text": message,
            "link": {
                "web_url": "https://news.naver.com",
                "mobile_web_url": "https://news.naver.com"
            },
            "button_title": "뉴스 보러가기"
        }
        
        data = {
            'template_object': json.dumps(template)
        }
        
        try:
            response = requests.post(
                self.message_url,
                headers=headers,
                data=data
            )
            response.raise_for_status()
            
            print("✅ 카카오톡 메시지 전송 성공")
            return True
        
        except requests.RequestException as e:
            print(f"❌ 카카오톡 메시지 전송 실패: {e}")
            
            # Access Token 만료 시 재시도
            if response.status_code == 401:
                print("🔄 Access Token 재발급 후 재시도...")
                if self.get_access_token():
                    return self.send_message(message)
            
            return False


if __name__ == "__main__":
    # 테스트 코드
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    client_id = os.getenv('KAKAO_CLIENT_ID')
    refresh_token = os.getenv('KAKAO_REFRESH_TOKEN')
    
    if client_id and refresh_token:
        sender = KakaoSender(client_id, refresh_token)
        test_message = "📰 테스트 메시지입니다!\n\n이것은 카카오톡 전송 테스트입니다."
        sender.send_message(test_message)
    else:
        print("❌ 환경 변수를 설정해주세요.")