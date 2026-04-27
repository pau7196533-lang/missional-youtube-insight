import io
import os
import re
import textwrap
from datetime import datetime
from html import escape
from pathlib import Path

import streamlit as st

try:
    import google.generativeai as genai
except ImportError:
    genai = None


APP_TITLE = "AI 유튜브 선교 인사이트 분석기"
DEFAULT_MODEL = "gemini-1.5-pro"

SYSTEM_INSTRUCTION = """
너는 세계적인 기독교 전략가이자 선교학 교수이다. 입력된 유튜브 내용을 바탕으로 다음 4가지 항목을 작성하라.

1. Table of Contents: 영상의 타임라인별 주요 목차.
2. Executive Summary: 영상 전체의 핵심 내용을 3문장으로 요약.
3. Core Argument: 저자가 주장하는 핵심 논지와 근거 기술.
4. Missional Application (핵심): 이 내용을 선교적 관점에서 재해석하라.
   - 이 메시지가 선교지 현장이나 유학생 사역에 어떻게 적용될 수 있는가?
   - 현대 선교 전략에 주는 시사점은 무엇인가?
   - 관련하여 묵상할 수 있는 성경 구절 1~2개를 매칭하라.

모든 답변은 한국어로 작성하되, 전문 용어는 영어 원어를 병기하라.
""".strip()

LENS_GUIDES = {
    "일반 문화": "대중문화, 세계관, 가치관, 세대 담론을 중심으로 분석하라.",
    "비즈니스 선교(BAM)": "Business as Mission, 직업 소명, 시장 선교, 창업과 선교 전략을 중심으로 분석하라.",
    "미전도 종족 선교": "Unreached People Groups, 접근 전략, 문화 적응, 복음 접촉점을 중심으로 분석하라.",
    "유학생 사역": "International Student Ministry, 캠퍼스 사역, 관계 전도, 제자화 관점으로 분석하라.",
    "디지털 선교": "Digital Mission, 온라인 공동체, 미디어 전략, 알고리즘 문화 관점으로 분석하라.",
}


def is_valid_youtube_url(url: str) -> bool:
    pattern = re.compile(
        r"^(https?://)?(www\.)?(youtube\.com/(watch\?v=|shorts/|embed/)|youtu\.be/)[A-Za-z0-9_\-]{6,}"
    )
    return bool(pattern.search(url.strip()))


def get_default_api_key() -> str:
    try:
        secret_key = st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("GEMINI_API_KEY")
    except Exception:
        secret_key = None
    return os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or secret_key or ""


def build_user_prompt(youtube_url: str, lens: str, extra_focus: str) -> str:
    focus_block = f"\n추가 분석 초점: {extra_focus.strip()}" if extra_focus.strip() else ""
    return f"""
분석 대상 유튜브 URL:
{youtube_url}

선택된 분석 렌즈:
{lens}

렌즈별 강조점:
{LENS_GUIDES[lens]}
{focus_block}

출력 형식은 아래 Markdown 구조를 반드시 따르라.

# 영상의 뼈대(Structure)

## 1. Table of Contents
- [00:00] ...

## 2. Executive Summary
1. ...
2. ...
3. ...

## 3. Core Argument
- 핵심 논지:
- 주요 근거:
- 전제와 함의:

# 영적 통찰(Missional Insight)

## 4. Missional Application
- 선교지 현장 적용:
- 유학생 사역 적용:
- 현대 선교 전략 시사점:
- 묵상 성경 구절:

## 5. 사역 적용 체크리스트
- ...
""".strip()


def analyze_youtube_video(api_key: str, youtube_url: str, lens: str, extra_focus: str, model_name: str) -> str:
    if genai is None:
        raise RuntimeError("google-generativeai 패키지가 설치되어 있지 않습니다. `pip install google-generativeai`를 실행해 주세요.")

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=SYSTEM_INSTRUCTION,
        generation_config={
            "temperature": 0.35,
            "top_p": 0.9,
            "max_output_tokens": 8192,
        },
    )

    prompt = build_user_prompt(youtube_url, lens, extra_focus)

    # Gemini API accepts public YouTube URLs as file_data parts.
    # The preview feature supports public videos only; private/unlisted videos may fail.
    video_part = {
        "file_data": {
            "file_uri": youtube_url,
            "mime_type": "video/*",
        }
    }

    response = model.generate_content([video_part, prompt])
    return response.text or "분석 결과가 비어 있습니다. 다른 영상이나 더 구체적인 분석 초점을 입력해 보세요."


def to_text_download(result: str, youtube_url: str, lens: str) -> bytes:
    header = f"""
{APP_TITLE}
생성 시각: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
유튜브 URL: {youtube_url}
분석 렌즈: {lens}

{"=" * 72}

""".lstrip()
    return (header + result).encode("utf-8")


def find_korean_font() -> str | None:
    candidates = [
        Path("C:/Windows/Fonts/malgun.ttf"),
        Path("C:/Windows/Fonts/malgunbd.ttf"),
        Path("/System/Library/Fonts/AppleSDGothicNeo.ttc"),
        Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


def to_pdf_download(result: str, youtube_url: str, lens: str) -> bytes:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    except ImportError as exc:
        raise RuntimeError("PDF 저장에는 reportlab이 필요합니다. `pip install reportlab`을 실행해 주세요.") from exc

    buffer = io.BytesIO()
    font_name = "Helvetica"
    font_path = find_korean_font()
    if font_path:
        font_name = "KoreanBody"
        pdfmetrics.registerFont(TTFont(font_name, font_path))

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "KoreanTitle",
        parent=styles["Title"],
        fontName=font_name,
        fontSize=17,
        leading=22,
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "KoreanBody",
        parent=styles["BodyText"],
        fontName=font_name,
        fontSize=10.5,
        leading=16,
        spaceAfter=7,
    )

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=APP_TITLE,
    )

    story = [
        Paragraph(escape(APP_TITLE), title_style),
        Paragraph(escape(f"생성 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"), body_style),
        Paragraph(escape(f"유튜브 URL: {youtube_url}"), body_style),
        Paragraph(escape(f"분석 렌즈: {lens}"), body_style),
        Spacer(1, 8),
    ]

    for raw_line in result.splitlines():
        line = raw_line.strip()
        if not line:
            story.append(Spacer(1, 5))
            continue
        if line.startswith("# "):
            story.append(Spacer(1, 7))
            story.append(Paragraph(f"<b>{escape(line[2:])}</b>", title_style))
        elif line.startswith("## "):
            story.append(Paragraph(f"<b>{escape(line[3:])}</b>", body_style))
        else:
            wrapped = "<br/>".join(escape(part) for part in textwrap.wrap(line, width=95) or [""])
            story.append(Paragraph(wrapped, body_style))

    doc.build(story)
    return buffer.getvalue()


def render_result(result: str) -> None:
    structure, insight = result, ""
    marker = "# 영적 통찰(Missional Insight)"
    if marker in result:
        structure, insight = result.split(marker, 1)
        insight = marker + insight

    left, right = st.columns(2, gap="large")
    with left:
        st.subheader("영상의 뼈대(Structure)")
        st.markdown(structure.replace("# 영상의 뼈대(Structure)", "").strip())
    with right:
        st.subheader("영적 통찰(Missional Insight)")
        st.markdown(insight.replace(marker, "").strip() if insight else "선교적 통찰 섹션을 찾지 못했습니다.")


def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title(APP_TITLE)
    st.caption("유튜브 영상의 구조를 정리하고 선교적 관점의 적용점을 도출합니다.")

    with st.sidebar:
        st.header("설정")
        default_api_key = get_default_api_key()
        if default_api_key:
            st.success("서버에 저장된 Gemini API 키를 사용합니다.")
            entered_api_key = st.text_input(
                "다른 Google Gemini API 키 사용",
                type="password",
                help="비워두면 서버 환경변수 또는 Streamlit secrets의 키를 사용합니다.",
            )
            api_key = entered_api_key or default_api_key
        else:
            api_key = st.text_input(
                "Google Gemini API 키",
                type="password",
                help="배포 환경에서는 GOOGLE_API_KEY, GEMINI_API_KEY 또는 Streamlit secrets를 권장합니다.",
            )
        model_name = st.text_input("모델명", value=DEFAULT_MODEL, help="요청 사양에 맞춰 기본값은 gemini-1.5-pro입니다.")
        lens = st.selectbox("분석 렌즈", list(LENS_GUIDES.keys()))
        extra_focus = st.text_area(
            "추가 분석 초점",
            placeholder="예: 청년 사역 적용, 현장 선교사 훈련, BAM 사례 발굴 등",
            height=110,
        )
        st.divider()
        st.info(
            "유튜브 URL 직접 분석은 공개 영상에서 동작합니다. 비공개 또는 일부 공개 영상은 Gemini API 제한으로 실패할 수 있습니다."
        )

    youtube_url = st.text_input(
        "유튜브 URL",
        placeholder="https://www.youtube.com/watch?v=...",
    )

    col_a, col_b = st.columns([1, 3])
    with col_a:
        analyze_clicked = st.button("분석 시작", type="primary", use_container_width=True)
    with col_b:
        st.write("")

    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = ""
        st.session_state.last_url = ""
        st.session_state.last_lens = lens

    if analyze_clicked:
        if not api_key:
            st.error("사이드바에 Google Gemini API 키를 입력해 주세요.")
        elif not youtube_url:
            st.error("분석할 유튜브 URL을 입력해 주세요.")
        elif not is_valid_youtube_url(youtube_url):
            st.error("올바른 유튜브 URL 형식인지 확인해 주세요.")
        else:
            with st.spinner("영상을 분석하는 중입니다. 긴 영상은 시간이 조금 걸릴 수 있습니다."):
                try:
                    result = analyze_youtube_video(api_key, youtube_url, lens, extra_focus, model_name.strip())
                    st.session_state.analysis_result = result
                    st.session_state.last_url = youtube_url
                    st.session_state.last_lens = lens
                    st.success("분석이 완료되었습니다.")
                except Exception as exc:
                    st.error(f"분석 중 오류가 발생했습니다: {exc}")
                    st.stop()

    if st.session_state.analysis_result:
        st.divider()
        render_result(st.session_state.analysis_result)

        st.divider()
        st.subheader("저장")
        download_name = f"missional_youtube_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        txt_bytes = to_text_download(
            st.session_state.analysis_result,
            st.session_state.last_url,
            st.session_state.last_lens,
        )

        dl_left, dl_right = st.columns(2)
        with dl_left:
            st.download_button(
                "텍스트 파일 저장",
                data=txt_bytes,
                file_name=f"{download_name}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with dl_right:
            try:
                pdf_bytes = to_pdf_download(
                    st.session_state.analysis_result,
                    st.session_state.last_url,
                    st.session_state.last_lens,
                )
                st.download_button(
                    "PDF 저장",
                    data=pdf_bytes,
                    file_name=f"{download_name}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except RuntimeError as exc:
                st.warning(str(exc))

    with st.expander("설치 및 실행 방법"):
        st.code(
            """
pip install streamlit google-generativeai reportlab
streamlit run streamlit_app.py
            """.strip(),
            language="bash",
        )
        st.markdown(
            "참고: 2026년 기준 Google 공식 문서는 신규 SDK인 `google-genai`를 권장하지만, "
            "이 예제는 요청 사양에 맞춰 `google-generativeai`를 사용합니다."
        )


if __name__ == "__main__":
    main()
