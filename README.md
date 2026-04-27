# AI 유튜브 선교 인사이트 분석기

유튜브 영상을 분석해 목차, 개요, 핵심 논지와 선교적 관점의 인사이트를 제공하는 Streamlit 앱입니다.

## 주요 기능

- 유튜브 URL 입력 및 Gemini 기반 분석
- 영상의 뼈대(Structure): 목차, 요약, 핵심 논지
- 영적 통찰(Missional Insight): 선교 현장, 유학생 사역, 현대 선교 전략 적용점
- TXT/PDF 다운로드
- Streamlit Community Cloud와 Google Cloud Run 배포 지원

## 로컬 실행

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Streamlit Community Cloud 설정

앱 생성 시 아래 값을 지정합니다.

```text
Main file path: streamlit_app.py
```

Secrets에는 아래 값을 등록합니다.

```toml
GEMINI_API_KEY = "Google AI Studio에서 발급한 API 키"
```

서버 Secret을 등록하지 않으면 사용자가 앱 사이드바에서 직접 Gemini API 키를 입력해 사용할 수 있습니다.

## GitHub 업로드 스크립트

GitHub CLI를 설치하고 로그인한 뒤 아래 명령으로 저장소 생성과 푸시를 실행할 수 있습니다.

```powershell
.\publish_to_github.ps1 -RepoName missional-youtube-insight -Visibility public
```
