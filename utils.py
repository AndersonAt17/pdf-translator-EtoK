import PyPDF2
import base64
import io


def extract_pages_from_pdf(file):
    """PDF에서 페이지 단위로 텍스트 추출"""
    file_bytes = io.BytesIO(file.read())
    reader = PyPDF2.PdfReader(file_bytes)
    return [page.extract_text() or "" for page in reader.pages]


def append_to_file(filename, content):
    """결과 파일에 번역 결과를 한 페이지씩 추가 저장"""
    with open(filename, "a", encoding="utf-8") as f:
        f.write(content)


def generate_download_link(text, filename="translated.txt"):
    """스트림릿에서 다운로드 링크 생성용 (사용 안 해도 됨)"""
    b64 = base64.b64encode(text.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">📥 번역된 문서 다운로드</a>'
