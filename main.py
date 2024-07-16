from fastapi import FastAPI, HTTPException, Request
from moviepy.editor import *
from fastapi.responses import FileResponse
from PIL import Image
from starlette.background import BackgroundTask
import numpy as np
import io
import re
import requests
import os
import json
import base64


app = FastAPI()
font_path = "font/NotoSansKR-Bold.ttf"


def download_image(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        return Image.open(io.BytesIO(response.content))
    else:
        raise Exception("Image download failed")


def wrap_text(text, font_size, max_width):
    text_clip = TextClip(text, fontsize=font_size, font=font_path)
    text_width, _ = text_clip.size
    if text_width <= max_width:
        return text

    words = text.split(' ')
    wrapped_text = words[0]
    for word in words[1:]:  # 단어수마다 텍스트클립을 만들어보기때문에 비효율적임
        test_clip = TextClip(wrapped_text + ' ' + word, fontsize=font_size, font=font_path)
        test_width, _ = test_clip.size
        if test_width <= max_width:
            wrapped_text += ' ' + word
        else:
            wrapped_text += '\n' + word
    return wrapped_text


def create_sound(text, model="ko-KR-Wavenet-C", speaking_rate=1.0):
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
            "name": model,  # Wavenet 음성 설정
            "ssmlGender": "NEUTRAL"
        },
        "audioConfig": {
            "audioEncoding": "MP3",
            "speakingRate": speaking_rate  # 속도 설정(클수록 빨라짐)
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    # 응답 상태 코드 출력
    print(f"Response status code: {response.status_code}")

    if response.status_code == 200:
        response_data = response.json()
        # 오디오 콘텐츠 확인
        audio_content = response_data.get('audioContent')
        if audio_content:
            output_path = f"TTS/voice{text}.mp3"
            with open(output_path, "wb") as out:
                out.write(base64.b64decode(audio_content))
            audio_length_sec = (len(audio_content) / 1000.0) # 미리초를 초로 변환
            return output_path, audio_length_sec
        else:
            print("No audio content received")
            return None, 0
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None, 0


def create_text_clip(text, fontsize, duration, position):  # TODO 텍스트가 창을 넘을 때 처리
    print(text, fontsize, duration, position)
    text_clip = TextClip(text, fontsize=fontsize, color='white', font=font_path)
    text_clip = text_clip.set_duration(duration)
    # 텍스트 클립 크기 계산
    text_width, text_height = text_clip.size
    # 검은 네모 상자 생성
    box_clip = ColorClip(size=(text_width + 20, text_height + 20), color=(0, 0, 0), duration=duration)
    # 네모 상자에 텍스트 클립 합성
    composite_clip = CompositeVideoClip([box_clip.set_position('center'), text_clip.set_position('center')])
    return composite_clip.set_position(position)


def make_video_clip(title, image, content):
    background_clip = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=10)
    if content is not None:  # 본문
        content_clip = create_text_clip(content, fontsize=90, duration=5, position=('center', 'bottom'))

        if image is not None:  # 이미지가 있을 때
            image_pil = download_image(image)
            image_clip = ImageClip(np.array(image_pil)).set_position('center').set_duration(10)
            video = CompositeVideoClip([background_clip, image_clip, content_clip])
        elif title is not None:  # 제목이 있을 때
            title_clip = create_text_clip(title, fontsize=100, duration=5, position='center')
            video = CompositeVideoClip([background_clip, content_clip, title_clip])
        else:  # 본문만 있을 때
            video = CompositeVideoClip([background_clip, content_clip])
        return video

    elif title is not None:  # 타이틀
        title_clip = create_text_clip(title, fontsize=100, duration=5, position=('center', 'bottom'))
        video = CompositeVideoClip([background_clip, title_clip])
        return video
    elif image is not None:  # 이미지
        image_pil = download_image(image)
        image_clip = ImageClip(np.array(image_pil)).set_position('center').set_duration(3)
        video = CompositeVideoClip([background_clip, image_clip])
        return video

    return None


@app.post("/markdown")
async def markdown(request: Request):
    try:
        text = await request.body()
        decoded_text = text.decode('utf-8')
        char_count = len(decoded_text)
        if char_count > 1000:
            raise HTTPException(status_code=400, detail=f"Text exceeds 1000 characters : {char_count}")

        text_lines = decoded_text.split('\n')
        pretitle = None
        preimage = None
        video_clips = []
        for line in text_lines:
            video_clip = None
            if line.startswith('#'):  # 타이틀일때
                preimage = None
                pretitle = re.sub(r'^[#]{1,3}', '', line).strip()  # #제거
                video_clip = make_video_clip(pretitle, None, None)
            elif line.startswith('!['):  # 이미지일때
                match = re.search(r'\((.*?)\)', line)  # url 파싱
                if match:
                    preimage = match.group(1)
                    video_clip = make_video_clip(None, preimage, None)
            else:  # 본문일때
                video_clip = make_video_clip(pretitle, preimage, line)
            if video_clips is not None:
                video_clips.append(video_clip)
            else:
                pass
        final_video = concatenate_videoclips(video_clips)
        output_filename = "markdownTest"
        # 비디오 파일 경로 설정
        output_filepath = f"video/{output_filename}.mp4"
        # 비디오 파일로 저장
        final_video.write_videofile(output_filepath, fps=24, codec='libx264', audio_codec='aac')
        def cleanup():
            if os.path.exists(output_filepath):
                os.remove(output_filepath)
        # 응답이 완료된 후 파일 삭제
        file_remove = BackgroundTask(cleanup)
        response = FileResponse(output_filepath, media_type='video/mp4', filename="markdownTest.mp4", background=file_remove)

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)