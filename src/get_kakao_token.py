"""
카카오 OAuth 토큰 발급 (Scope 강제 포함 버전)
"""

import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import requests


class OAuthHandler(BaseHTTPRequestHandler):
    authorization_code = None
    
    def do_GET(self):
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        if 'code' in params:
            OAuthHandler.authorization_code = params['code'][0]
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            success_html = """
            <html>
            <head><meta charset="utf-8"></head>
            <body style="font-family: Arial; padding: 50px; text-align: center;">
                <h1 style="color: #4CAF50;">✅ 인증 성공!</h1>
                <p style="font-size: 18px;">이제 이 창을 닫고 터미널로 돌아가세요.</p>
                <p style="color: #666; font-size: 14px;">권한 동의를 완료했는지 확인하세요!</p>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode('utf-8'))
        else:
            self.send_response(400)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass


def get_authorization_code(client_id: str, redirect_uri: str) -> str:
    # SCOPE를 명시적으로 포함
    scopes = [
        'talk_message',  # 카카오톡 메시지 전송
    ]
    scope_string = ','.join(scopes)
    
    auth_url = (
        f"https://kauth.kakao.com/oauth/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope={scope_string}"  # 명시적 scope 포함
    )
    
    print("\n" + "="*70)
    print("📱 카카오 로그인 페이지를 여는 중...")
    print("="*70)
    print("\n⚠️  중요: 브라우저에서 반드시 다음을 확인하세요!")
    print("   1. 카카오 로그인")
    print("   2. 권한 동의 화면에서 '카카오톡 메시지 전송' 체크 ✅")
    print("   3. '동의하고 계속하기' 클릭")
    print("="*70)
    
    webbrowser.open(auth_url)
    
    server = HTTPServer(('localhost', 8000), OAuthHandler)
    print("\n⏳ 카카오 로그인을 완료하고 권한을 승인해주세요...")
    print("   브라우저가 자동으로 열리지 않으면 아래 URL을 복사하세요:")
    print(f"\n   {auth_url}\n")
    
    server.handle_request()
    
    return OAuthHandler.authorization_code


def get_tokens(client_id: str, client_secret: str, redirect_uri: str, authorization_code: str) -> dict:
    token_url = "https://kauth.kakao.com/oauth/token"
    
    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'code': authorization_code
    }
    
    if client_secret:
        data['client_secret'] = client_secret
    
    print("\n🔄 토큰 발급 요청 중...")
    
    response = requests.post(token_url, data=data)
    
    if response.status_code != 200:
        print(f"\n❌ 토큰 발급 실패 (HTTP {response.status_code})")
        print(f"\n📋 응답 내용:")
        print(response.text)
        
        try:
            error_info = response.json()
            print(f"\n🔍 상세 정보:")
            print(f"   에러 코드: {error_info.get('error', 'Unknown')}")
            print(f"   에러 설명: {error_info.get('error_description', 'No description')}")
        except:
            pass
        
        response.raise_for_status()
    
    tokens = response.json()
    
    # Scope 확인
    if 'scope' in tokens:
        print(f"\n✅ 부여된 권한(Scope): {tokens['scope']}")
        if 'talk_message' not in tokens['scope']:
            print("\n⚠️  경고: 'talk_message' 권한이 포함되지 않았습니다!")
            print("   토큰 재발급 시 권한 동의를 다시 확인하세요.")
    
    return tokens


def main():
    print("\n" + "="*70)
    print("🔑 카카오 OAuth 토큰 발급 (Scope 포함)")
    print("="*70)
    
    client_id = input("\n📌 카카오 REST API 키를 입력하세요: ").strip()
    
    if not client_id:
        print("❌ REST API 키가 입력되지 않았습니다.")
        return
    
    print("\n📌 Client Secret이 있나요?")
    print("   (카카오 개발자 콘솔 → 앱 설정 → 보안 → Client Secret)")
    has_secret = input("   있으면 'y', 없으면 Enter: ").strip().lower()
    
    client_secret = ""
    if has_secret == 'y':
        client_secret = input("   Client Secret을 입력하세요: ").strip()
    
    redirect_uri = "http://localhost:8000/callback"
    
    print("\n" + "="*70)
    print("📋 설정 확인")
    print("="*70)
    print(f"   Client ID: {client_id[:10]}...{client_id[-4:]}")
    if client_secret:
        print(f"   Client Secret: {'*' * 20}")
    print(f"   Redirect URI: {redirect_uri}")
    print(f"   Scope: talk_message (카카오톡 메시지 전송)")
    
    print("\n⚠️  카카오 개발자 콘솔 설정 재확인!")
    print("="*70)
    print("1. [카카오 로그인] → 활성화: ON")
    print("2. [카카오 로그인] → Redirect URI:")
    print(f"   → {redirect_uri} (정확히 일치)")
    print("3. [동의항목] → 카카오톡 메시지 전송:")
    print("   → '필수 동의' 또는 '선택 동의' 설정됨")
    print("="*70)
    
    input("\n✅ 설정을 확인했으면 Enter를 누르세요...")
    
    try:
        # 1. Authorization Code 획득
        auth_code = get_authorization_code(client_id, redirect_uri)
        
        if not auth_code:
            print("\n❌ Authorization Code를 받지 못했습니다.")
            return
        
        print(f"\n✅ Authorization Code 획득: {auth_code[:20]}...")
        
        # 2. 토큰 발급
        tokens = get_tokens(client_id, client_secret, redirect_uri, auth_code)
        
        # 3. 결과 출력
        print("\n" + "="*70)
        print("🎉 토큰 발급 완료!")
        print("="*70)
        print(f"\n✅ Access Token: {tokens['access_token'][:30]}...")
        print(f"✅ Refresh Token: {tokens['refresh_token']}")
        print(f"✅ 유효기간: {tokens['expires_in']}초 (~{tokens['expires_in']//3600}시간)")
        
        if 'refresh_token_expires_in' in tokens:
            days = tokens['refresh_token_expires_in'] // 86400
            print(f"✅ Refresh Token 유효기간: {days}일")
        
        # .env 파일 생성
        print("\n" + "="*70)
        print("📝 환경 변수 설정")
        print("="*70)
        
        env_content = f"""# 카카오 API 설정
KAKAO_CLIENT_ID={client_id}
KAKAO_REFRESH_TOKEN={tokens['refresh_token']}
"""
        
        if client_secret:
            env_content += f"KAKAO_CLIENT_SECRET={client_secret}\n"
        
        print(env_content)
        
        create_env = input("\n.env 파일을 자동으로 생성/덮어쓰기 할까요? (y/n): ").strip().lower()
        
        if create_env == 'y':
            with open('.env', 'w', encoding='utf-8') as f:
                f.write(env_content)
            print("\n✅ .env 파일이 생성되었습니다!")
        
        print("\n" + "="*70)
        print("✅ 모든 설정이 완료되었습니다!")
        print("="*70)
        print("\n다음 명령어로 테스트하세요:")
        print("   python src/main.py")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()