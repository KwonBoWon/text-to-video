from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from moviepy.editor import *
from fastapi.responses import FileResponse
from PIL import Image
import numpy as np
import io

app = FastAPI()


@app.post("/video")
async def upload_photo(text: str = Form(...), image: UploadFile = File(...), output_filename: str = Form(...)):
    try:
        # 이미지 파일을 메모리에서 읽기
        image_data = await image.read()
        image_pil = Image.open(io.BytesIO(image_data))

        # 배경 크기를 1920x1080으로 설정하는 비디오 클립 생성
        background_clip = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=10)

        # PIL 이미지를 ImageClip으로 변환
        image_clip = ImageClip(np.array(image_pil)).set_position('center').set_duration(10).fadein(1).fadeout(1)

        # 텍스트 클립 생성 (폰트, 그림자 추가)
        txt_clip = TextClip(text, fontsize=70, color='white', font='Amiri-Bold', stroke_color='black', stroke_width=2)
        txt_clip = txt_clip.set_duration(10).set_position(('center', 'bottom')).crossfadein(1).crossfadeout(1)

        # 배경에 이미지와 텍스트를 합성
        video = CompositeVideoClip([background_clip, image_clip, txt_clip])

        # 비디오 파일 경로 설정
        output_filepath = f"video/{output_filename}.mp4"

        # 비디오 파일로 저장
        video.write_videofile(output_filepath, fps=24, codec='libx264', audio_codec='aac')

        # 생성된 동영상 파일을 HTTP 응답으로 반환
        return FileResponse(output_filepath, media_type='video/mp4', filename=output_filename + '.mp4')

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/photo")
async def upload_photo(text: str = Form(...), image: UploadFile = File(...), output_filename: str = Form(...)):
    UPLOAD_DIR = "photo"  # 이미지를 저장할 서버 경로

    content = await image.read()
    # filename = f"{str(uuid.uuid4())}.jpg"  # uuid로 유니크한 파일명으로 변경
    filename = f"{str(output_filename)}.jpg"  # uuid로 유니크한 파일명으로 변경
    with open(os.path.join(UPLOAD_DIR, filename), "wb") as fp:
        fp.write(content)  # 서버 로컬 스토리지에 이미지 저장 (쓰기)

    return {"filename": filename}

