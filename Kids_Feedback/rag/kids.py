#  임포트 걱정 없으니 바로 가자. rag_docs/위축형_칭찬법.md 읽어서 .split("##") 한 다음 print로
#   찍어봐. 쳐와!

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") #변수명으로 값꺼냄

client = genai.Client(api_key=api_key)

# 왜 밖에 두는 게 맞냐 다시 짚자면: 키 읽기랑 점원 부르기는 프로그램 켤 때 딱 한 번만 하면 돼.

def embed_feedback(prompt):
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=prompt,
          # ```json 없이 순수 JSON만 받기
    )
    return response.embeddings[0].values
    embed(response)

#아래만 있으면 rag_docs 있는답 그대로 나옴

with open("rag_docs/위축형_칭찬법.md", "r",encoding="utf-8") as f:
    text = f.read()
chunking= text.split("##")

chunks = []
for c in chunking[1:]:
    chunks.append(c.strip())
print(len(chunks))
print(chunks[0])





