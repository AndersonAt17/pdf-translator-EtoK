import streamlit as st

# ✅ 가장 먼저 Streamlit 설정
st.set_page_config(page_title="PDF 번역기", layout="centered")

from translator import translate_page, get_translation_footer
from utils import extract_pages_from_pdf, append_to_file
from dotenv import load_dotenv
from streamlit_cookies_manager import EncryptedCookieManager
import os

# ✅ 환경변수 로드
load_dotenv()
USERNAME = os.getenv("LOGIN_USER")
PASSWORD = os.getenv("LOGIN_PASS")
COOKIE_SECRET = os.getenv("COOKIE_SECRET", "default_cookie_secret")

# ✅ 쿠키 매니저 초기화
cookies = EncryptedCookieManager(prefix="login_", password=COOKIE_SECRET)
if not cookies.ready():
    st.stop()

# ✅ 로그아웃 여부 세션 확인
logout_triggered = st.session_state.get("force_logout", False)

# ✅ 로그인 상태 판단 (쿠키 기반 + 세션 보완)
logged_in = (
    cookies.get("logged_in", default="false").strip().lower() == "true"
    and cookies.get("username") not in [None, "", "null"]
    and not logout_triggered
)

username = cookies.get("username")

# ✅ 로그인 화면
if not logged_in:
    st.title("🔐 로그인")
    input_username = st.text_input("아이디", key="username_input")
    input_password = st.text_input("비밀번호", type="password", key="password_input")

    if st.button("로그인"):
        if input_username == USERNAME and input_password == PASSWORD:
            cookies["logged_in"] = "true"
            cookies["username"] = input_username
            cookies.save()
            st.session_state["force_logout"] = False
            st.success("✅ 로그인 성공! 페이지를 새로고침합니다.")
            st.rerun()
        else:
            st.error("❌ 아이디 또는 비밀번호가 틀렸습니다.")
    st.stop()

# ✅ 로그아웃 처리
if st.button("로그아웃"):
    cookies["logged_in"] = ""  # 빈 값으로 덮어쓰기
    cookies["username"] = ""
    cookies.save()
    st.session_state["force_logout"] = True
    st.experimental_set_query_params(logout="true")
    st.success("로그아웃 완료. 새로고침합니다.")
    st.stop()

# ✅ 로그인된 사용자 화면
st.title("📘 대용량 PDF 번역기")
st.markdown(f"👤 로그인된 사용자: `{username}`")

uploaded_file = st.file_uploader("📤 PDF 파일 업로드", type=["pdf"])

if uploaded_file:
    file_name = uploaded_file.name
    st.info(f"파일 이름: `{file_name}`")

    with st.spinner("🔍 페이지 텍스트 추출 중..."):
        try:
            pages = extract_pages_from_pdf(uploaded_file)
            st.success(f"총 {len(pages)}페이지 텍스트 추출 완료")
        except Exception as e:
            st.error(f"❌ PDF 추출 오류: {e}")
            st.stop()

    output_path = "translated_output.txt"
    if os.path.exists(output_path):
        os.remove(output_path)

    if st.button("🔁 전체 번역 시작"):
        with st.spinner("🧠 번역 중입니다..."):
            for i, page_text in enumerate(pages):
                st.write(f"📄 Page {i+1} 번역 중...")
                if page_text.strip():
                    translated = translate_page(page_text, i + 1)
                else:
                    translated = f"[빈 페이지]\n\n---\n📄 원문 출처: Page {i + 1}"
                append_to_file(output_path, translated + "\n\n")
                st.progress((i + 1) / len(pages))

            summary = get_translation_footer()
            append_to_file(output_path, summary)
            st.success("✅ 전체 번역 완료!")

        with open(output_path, "rb") as f:
            st.download_button("📥 번역된 파일 다운로드", f, file_name=output_path)
