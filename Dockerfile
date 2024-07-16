# 베이스 이미지 설정
FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# 의존성 파일 복사 및 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY . /app

# 환경 변수 설정
ENV APP_ENV=production

# FastAPI 애플리케이션 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
