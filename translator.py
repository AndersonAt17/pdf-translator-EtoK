import os
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
MAX_LENGTH = 3000


def truncate_text(text, max_length=MAX_LENGTH):
    if len(text) > max_length:
        return text[:max_length] + "\n[이후 생략됨]"
    return text


def translate_with_google(text):
    try:
        return GoogleTranslator(source="auto", target="ko").translate(text)
    except Exception as e:
        raise RuntimeError(f"Google 번역 실패: {e}")


def translate_with_openai(text):
    chat = ChatOpenAI(openai_api_key=openai_key, temperature=0.3)
    truncated = truncate_text(text)
    response = chat([HumanMessage(content=f"Translate to Korean:\n\n{truncated}")])
    return response.content.strip()


def translate_page(text, page_num):
    try:
        translated = translate_with_google(text)
    except Exception as e:
        try:
            translated = translate_with_openai(text)
        except Exception as oe:
            return "[번역 실패]"
    return f"{translated}\n\n---\n📄 원문 출처: Page {page_num}"
