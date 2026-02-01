# 네이버 뉴스 카카오톡 자동 발송 봇

네이버 뉴스를 크롤링하여 카카오톡으로 자동으로 전송하는 봇입니다.

## 기능

- 네이버 뉴스 속보 페이지에서 상위 10개 기사 크롤링
- 카카오톡 '나에게 보내기' 기능을 통한 메시지 전송

## 사전 준비

1. 카카오 개발자 계정 및 앱 등록
2. 카카오 REST API 키 발급
3. 카카오톡 로그인 및 Refresh Token 발급

## 환경 변수 설정

`.env` 파일을 생성하고 다음 변수를 설정하세요:

```env
KAKAO_CLIENT_ID=your_kakao_client_id
KAKAO_REFRESH_TOKEN=your_kakao_refresh_token
```

## Docker를 사용한 실행 방법

### 1. Docker 이미지 빌드

```bash
docker build -t naver-news-bot .
```

### 2. 환경 변수 설정

`.env` 파일을 생성하거나 환경 변수를 직접 설정합니다.

### 3. Docker Compose를 사용한 실행 (권장)

```bash
docker-compose up
```

또는 백그라운드 실행:

```bash
docker-compose up -d
```

### 4. Docker 명령어로 직접 실행

```bash
docker run --rm \
  --env-file .env \
  naver-news-bot
```

또는 환경 변수를 직접 지정:

```bash
docker run --rm \
  -e KAKAO_CLIENT_ID=your_client_id \
  -e KAKAO_REFRESH_TOKEN=your_refresh_token \
  naver-news-bot
```

## 프로젝트 구조

```
naver-news-kakao-bot/
├── src/
│   ├── main.py          # 메인 실행 파일
│   ├── crawler.py       # 네이버 뉴스 크롤러
│   ├── kakao_sender.py  # 카카오톡 메시지 전송
│   └── test_crawler.py  # 테스트 파일
├── Dockerfile           # Docker 이미지 설정
├── docker-compose.yml   # Docker Compose 설정
├── requirements.txt     # Python 의존성
└── README.md           # 프로젝트 설명
```

## 문제 해결

### Docker 실행 시 환경 변수 오류

`.env` 파일이 올바르게 설정되었는지 확인하세요:

```bash
cat .env
```

### 네트워크 연결 오류

가상머신에서 인터넷 연결을 확인하세요:

```bash
ping google.com
```

### 권한 오류

Docker를 sudo 없이 사용하려면:

```bash
sudo usermod -aG docker $USER
newgrp docker
```
