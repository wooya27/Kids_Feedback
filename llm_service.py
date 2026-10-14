# 하는 일: 그 주문서를 Gemini에 보내고 답을 받아옴
#   비유: 주방에 주문 넣고 음식 받기



import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") #변수명으로 값꺼냄

client = genai.Client(api_key=api_key)

# 왜 밖에 두는 게 맞냐 다시 짚자면: 키 읽기랑 점원 부르기는 프로그램 켤 때 딱 한 번만 하면 돼.

def generate_feedback(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={"response_mime_type": "application/json"},  # ```json 없이 순수 JSON만 받기
    )
    return response.text

# client.models.generate_content(...)   → ① Gemini한테 프롬프트 보내기 (주문)
# 이 정보 + 수업 기록  →  [AI가 피드백 글을 써줌]  →강사/학부모에게 보여줌

#  prompt_service는 글만 만들어 놓을 뿐, AI를 부르진 않아. 누군가
#   그 글을 실제로 Gemini한테 들고 가서 "이거 보고 피드백 써줘" 해야
#   하잖아. 그 심부름꾼이 generate_feedback(prompt) 함수야.


#   return을 하는 이유: 이 글을 나중에 DB에 저장하고(Day 5) 화면에
#   보여줘야(Day 11) 하니까. 화면에 한 번 찍고 버리는 print가
#   아니라, 값을 다음 단계로 넘기려고 return 하는 거야. (어제
#   day4.md에 print vs return 적어둔 거 기억나지?)

# prompt_service가 만든 주문서를 실제로 Gemini한테 보내서 피드백 
# 글을 받아오는 담당이 generate_feedback 함수다.


# print(generate_feedback("줄넘기 10개 한 8살 아이에게 짧은 격려한마디 써줘"))
