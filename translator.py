import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import tiktoken

load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
MAX_LENGTH = 3000
MODEL_NAME = "gpt-4o"  # 모델명은 gpt-3.5-turbo, gpt-4, gpt-4o 중 선택

MODEL_PRICING = {
    "gpt-3.5-turbo": 0.0015,  # input 기준, per 1000 tokens
    "gpt-4": 0.03,
    "gpt-4o": 0.005,
}

# 전체 토큰수 누적용 전역 변수
total_tokens_used = 0


def truncate_text(text, max_length=MAX_LENGTH):
    if len(text) > max_length:
        return text[:max_length] + "\n[이후 생략됨]"
    return text


def count_tokens(text, model=MODEL_NAME):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def estimate_cost(token_count, model=MODEL_NAME):
    cost_per_1k = MODEL_PRICING.get(model, 0)
    return round((token_count / 1000) * cost_per_1k, 6)


def translate_with_openai(text):
    global total_tokens_used

    chat = ChatOpenAI(openai_api_key=openai_key, temperature=0.3, model=MODEL_NAME)
    truncated = truncate_text(text)

    tokens_used = count_tokens(truncated)
    total_tokens_used += tokens_used

    response = chat([HumanMessage(content=f"Translate to Korean:\n\n{truncated}")])
    return response.content.strip()


def translate_page(text, page_num):
    try:
        translated = translate_with_openai(text)
    except Exception:
        return "[번역 실패]"
    return f"{translated}\n\n---\n📄 원문 출처: Page {page_num}"


def get_translation_footer():
    global total_tokens_used
    total_cost = estimate_cost(total_tokens_used)
    return f"\n\n\n======== 번역 정보 요약 ========\n총 사용 토큰 수: {total_tokens_used} tokens\n총 추정 요금: ${total_cost} (모델: {MODEL_NAME})\n==============================="
