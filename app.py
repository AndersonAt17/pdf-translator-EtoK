import streamlit as st
from translator import translate_page
from utils import extract_pages_from_pdf, append_to_file
import os
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="PDF 번역기", layout="centered")
st.title("📘 대용량 PDF 번역기")

uploaded_file = st.file_uploader("📤 PDF 파일 업로드", type=["pdf"])

if uploaded_file:
    st.subheader("📑 업로드한 파일 보기")
    file_name = uploaded_file.name
    st.info(f"파일 이름: `{file_name}`")

    with st.spinner("🔍 페이지 텍스트 추출 중..."):
        try:
            pages = extract_pages_from_pdf(uploaded_file)
            st.success(f"총 {len(pages)}페이지 텍스트 추출 완료")
        except Exception as e:
            st.error(f"❌ PDF 추출 오류: {e}")
            st.stop()

    # 출력 파일 초기화
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
            st.success("✅ 전체 번역 완료!")

        with open(output_path, "rb") as f:
            st.download_button("📥 번역된 파일 다운로드", f, file_name=output_path)
