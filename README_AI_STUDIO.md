# Google AI Studio 프로젝트 연결 안내

이 Streamlit 앱은 Google AI Studio에서 발급한 Gemini API 키를 사용해 실행됩니다. Gemini API의 현재 유튜브 URL 입력 방식에 맞춰 `google-genai` SDK와 Gemini 2.5 계열 모델을 사용합니다.

## 1. AI Studio 프로젝트 준비

1. [Google AI Studio](https://aistudio.google.com/)에 로그인합니다.
2. Dashboard에서 `Projects`를 엽니다.
3. 기존 Google Cloud 프로젝트가 보이지 않으면 `Import projects`로 프로젝트를 가져옵니다.
4. `API Keys` 페이지에서 해당 프로젝트의 Gemini API 키를 생성하거나 확인합니다.

## 2. 로컬 실행

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

앱 사이드바에 API 키를 직접 입력할 수 있습니다.

## 3. 환경변수로 키 연결

PowerShell:

```powershell
$env:GEMINI_API_KEY="your_google_ai_studio_api_key_here"
python -m streamlit run streamlit_app.py
```

또는 `GOOGLE_API_KEY`를 사용할 수 있습니다. 두 값이 모두 있으면 앱은 `GOOGLE_API_KEY`를 우선 사용합니다.

## 4. 참고

- Google AI Studio의 프로젝트는 Gemini API 키가 연결되는 Google Cloud 프로젝트입니다.
- 공개 YouTube 영상 URL만 Gemini API의 직접 영상 분석 입력으로 사용할 수 있습니다.
- 비공개 또는 일부 공개 영상은 API 제한으로 실패할 수 있습니다.
- Google 공식 문서는 신규 앱에 `google-genai` SDK 사용을 권장합니다.
