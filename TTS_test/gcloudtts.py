import os
import requests
import json
import base64


def synthesize_text(text):
    api_key = os.getenv("GOOGLE_CLOUD_API_KEY")
    if not api_key:
        raise ValueError("API key not found in environment variables")

    url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={api_key}"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "input": {"text": text},
        "voice": {
            "languageCode": "ko-KR",
            "name": "ko-KR-Wavenet-C",  # Wavenet 음성 설정
            "ssmlGender": "NEUTRAL"
        },
        "audioConfig": {"audioEncoding": "MP3"}
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    # 응답 상태 코드 출력
    print(f"Response status code: {response.status_code}")

    if response.status_code == 200:
        response_data = response.json()

        # 오디오 콘텐츠 확인
        audio_content = response_data.get('audioContent')
        if audio_content:
            with open("outputC-1.mp3", "wb") as out:
                out.write(base64.b64decode(audio_content))
            print('Audio content written to file "output.mp3"')
            print(f"Audio Length{len(audio_content)}")
        else:
            print("No audio content received")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    api_key = os.getenv("GOOGLE_CLOUD_API_KEY")
    if api_key:
        print("API key is set")
        text = "안녕하세요, Google Cloud Text-to-Speech API를 사용한 예제입니다."
        synthesize_text(text)
    else:
        print("API key is not set")
