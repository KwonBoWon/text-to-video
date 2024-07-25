from gtts import gTTS
import os

# 변환할 텍스트
text = "안녕하세요, gTTS를 사용한 예제입니다."

# gTTS 객체 생성 (언어는 한국어 'ko'로 설정)
tts = gTTS(text=text, lang='ko', slow=False)

# 음성 파일로 저장
output_path = "output.mp3"
tts.save(output_path)

# 파일 재생 (macOS나 Linux에서)
os.system(f"mpg321 {output_path}")

print(f"변환된 음성이 {output_path}에 저장되었습니다.")
