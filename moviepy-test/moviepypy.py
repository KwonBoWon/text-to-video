from moviepy.editor import *

# 이미지 파일 경로
image_path = "moviepy-test/tts.png"

# 텍스트 클립 생성
text = "This project convert text to video"

# 텍스트 클립 생성 (폰트, 그림자 추가)
txt_clip = TextClip(text, fontsize=70, color='white', font='Amiri-Bold', stroke_color='black', stroke_width=2)
txt_clip = txt_clip.set_duration(10).set_position(('center', 'bottom')).crossfadein(1).crossfadeout(1)
# 이미지 클립 생성
image_clip = ImageClip(image_path).set_duration(10)

# 텍스트 클립을 이미지 위에 합성
video = CompositeVideoClip([image_clip, txt_clip])

# 비디오 파일로 출력
video.write_videofile("moviepy-test/output.mp4", fps=24)
