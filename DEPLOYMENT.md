# 배포 안내

이 앱은 Streamlit 앱이므로 가장 쉬운 공개 배포는 Streamlit Community Cloud이고, 소유 도메인까지 연결하려면 Google Cloud Run 같은 컨테이너 호스팅을 권장합니다.

## 옵션 A. 가장 빠른 공개 공유: Streamlit Community Cloud

장점: 무료 시작, GitHub 저장소만 있으면 몇 분 안에 `https://원하는이름.streamlit.app` 주소로 공유 가능.

1. 이 폴더를 GitHub 저장소에 업로드합니다.
2. [Streamlit Community Cloud](https://share.streamlit.io/)에서 `Create app`을 누릅니다.
3. 저장소, 브랜치, 엔트리포인트를 아래처럼 지정합니다.

```text
Main file path: streamlit_app.py
```

4. Advanced settings의 Secrets에 아래 값을 넣습니다.

```toml
GEMINI_API_KEY = "Google AI Studio에서 발급한 키"
```

5. App URL에 원하는 하위 도메인을 입력합니다.

```text
missional-youtube-insight.streamlit.app
```

Streamlit Community Cloud는 자체 `streamlit.app` 하위 도메인을 제공합니다. 개인 소유 도메인 연결이 꼭 필요하면 옵션 B를 사용하세요.

## 옵션 B. 개인 도메인까지 연결: Google Cloud Run

장점: `analysis.example.com` 같은 소유 도메인 연결 가능, 확장성 좋음.

사전 준비:

- Google Cloud 프로젝트
- 결제 계정
- Google Cloud CLI
- 소유 중인 도메인
- Gemini API 키

배포 명령 예시:

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com

gcloud run deploy missional-youtube-insight \
  --source . \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

배포가 끝나면 `https://...run.app` 주소가 생성됩니다.

도메인 연결:

1. Google Cloud Console에서 Cloud Run 서비스를 엽니다.
2. `Manage custom domains` 또는 Load Balancer/Firebase Hosting 경로로 도메인을 연결합니다.
3. Google이 안내하는 DNS 레코드를 도메인 등록기관 DNS에 추가합니다.
4. 인증서 발급과 DNS 전파가 완료되면 개인 도메인으로 접속할 수 있습니다.

Google Cloud 문서 기준으로 Cloud Run 도메인 연결은 다음 방식이 있습니다.

- Global external Application Load Balancer: 권장
- Firebase Hosting
- Cloud Run domain mapping: 제한/프리뷰 제공 지역 있음

## 보안 메모

- `.env`, `.streamlit/secrets.toml`은 저장소에 올리지 마세요.
- 배포 서비스의 Secret/Environment Variables에 `GEMINI_API_KEY`를 저장하세요.
- 공개 앱으로 운영하면 방문자가 서버 API 키를 사용해 분석을 실행할 수 있으므로 할당량과 비용을 모니터링하세요.
