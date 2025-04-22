from googletrans import Translator

# Translator 객체 생성
translator = Translator()

# 번역할 텍스트
text = "Hello, how are you?"

# 번역 실행 (목표 언어: 한국어 'ko')
result = translator.translate(text, dest="ko")

# 결과 출력
print("원문:", text)
print("번역:", result.text)
