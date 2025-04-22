import fitz  # PyMuPDF
from pdf2image import convert_from_bytes
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import cv2
import numpy as np
import textwrap
from translator import translate_page


def advanced_preprocess(pil_image: Image.Image) -> Image.Image:
    """
    OCR 정확도 향상을 위한 고급 이미지 전처리
    - 흑백 변환 + adaptive threshold 적용
    """
    img = np.array(pil_image.convert("L"))  # Grayscale
    processed = cv2.adaptiveThreshold(
        img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2
    )
    return Image.fromarray(processed)


def extract_text_with_fallback(page, image=None, page_num=1):
    """
    텍스트 기반 추출 → 실패 시 OCR로 자동 전환
    - OCR 결과는 로그로 출력됨
    """
    try:
        text = page.get_text("text")
        if text.strip():
            print(f"[Page {page_num}] ✅ 텍스트 기반 추출 성공")
            return text
        else:
            raise ValueError("텍스트 없음")
    except:
        if image is not None:
            processed_img = advanced_preprocess(image)
            ocr_text = pytesseract.image_to_string(processed_img, lang="eng")
            print(f"[Page {page_num}] 🔁 OCR 결과:\n{ocr_text[:300]}...\n")
            return ocr_text
        else:
            return "[텍스트 추출 실패 및 이미지 없음]"


def translate_pdf_with_layout(file, output_path="translated_output_final.pdf"):
    """
    전략 C 통합 최종 버전: 텍스트 기반 + OCR fallback 자동 처리
    """
    doc = fitz.open(stream=file.read(), filetype="pdf")

    # OCR을 위한 이미지 생성
    file.seek(0)
    images = convert_from_bytes(file.read(), dpi=300)

    translated_doc = fitz.open()

    for page_num, page in enumerate(doc, start=1):
        image = images[page_num - 1] if page_num <= len(images) else None
        extracted_text = extract_text_with_fallback(page, image, page_num)

        if not extracted_text.strip():
            translated = "[번역할 텍스트 없음]"
        else:
            try:
                translated = translate_page(extracted_text, page_num)
            except:
                translated = "[번역 실패]"

        # 텍스트 줄 단위 나누기
        wrapped_lines = textwrap.wrap(translated, width=100)

        # 출력 페이지 설정
        page_width, page_height = 595, 842
        font_size = 11
        line_spacing = font_size + 5
        margin_x = 50
        current_y = 50
        max_y = page_height - 50

        new_page = translated_doc.new_page(width=page_width, height=page_height)

        for line in wrapped_lines:
            if current_y + line_spacing > max_y:
                new_page = translated_doc.new_page(width=page_width, height=page_height)
                current_y = 50

            new_page.insert_text(
                (margin_x, current_y),
                line,
                fontsize=font_size,
                fontname="helv",
                color=(0, 0, 0),
            )
            current_y += line_spacing

    translated_doc.save(output_path)
    translated_doc.close()
