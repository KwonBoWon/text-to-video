from moviepy.editor import *


def make_audio():
    text = "오디오 클립이"
    font_size = 90
    font_path = "font/NotoSansKR-Bold.ttf"
    audio_path = "TTS/voice오디오 클립이.mp3"
    audio_clip = AudioFileClip(audio_path)
    clip_duration = audio_clip.duration

    background_clip = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=clip_duration)
    content_clip = TextClip(text, fontsize=font_size, color='white', font=font_path)
    content_clip = content_clip.set_duration(clip_duration).set_position('center')

    video = CompositeVideoClip([background_clip, content_clip])
    video = video.set_audio(audio_clip)

    print(video.audio.duration)
    video.write_videofile("video/오디오 클립이.mp4", fps=24)
    return

def add_audio2():
    # 비디오 클립 로드
    video_clip = VideoFileClip("video/오디오클립이.mp4")
    # 오디오 클립 로드
    audio_clip = AudioFileClip("TTS/voice오디오 클립이.mp3")
    # 비디오 클립에 오디오 클립 추가
    final_clip = video_clip.set_audio(audio_clip)
    # 최종 비디오 파일 저장
    final_clip.write_videofile("output_with_audio.mp4", fps=24, codec="libx264", audio_codec="aac")
    return

if __name__ == "__main__":
    make_audio()
