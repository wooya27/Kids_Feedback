# Dockerfile = "실행환경을 만드는 설명서"
# 다른 PC에도 이 순서대로 하면 똑같은 환경이 생긴다.

# 1) 바탕: 파이썬 3.13이 깔린 가벼운 리눅스
FROM python:3.13-slim

# 2) 컨테이너 안 작업 폴더
WORKDIR /app

# 3) 패키지 목록 먼저 복사 → 설치
#    (코드보다 먼저 복사하는 이유: 목록이 안 바뀌면 설치 단계를 캐시로 건너뛰어 빌드가 빨라짐)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) 나머지 소스 전부 복사
COPY . .

# 5) 이 컨테이너가 쓸 포트 (문서용 표시)
EXPOSE 8000

# 6) 컨테이너 켜질 때 실행할 명령
#    --host 0.0.0.0 = 컨테이너 밖에서도 접속 허용 (localhost만 쓰면 밖에서 못 들어옴)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
