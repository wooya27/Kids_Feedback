#  임포트 걱정 없으니 바로 가자. rag_docs/위축형_칭찬법.md 읽어서 .split("##") 한 다음 print로
#   찍어봐. 쳐와!

import os
from dotenv import load_dotenv
from google import genai
import json

load_dotenv("Kids_Feedback/.env")   # .env는 안쪽 폴더에 있음. 경로는 27번 줄과 같은 기준(바깥 Kids_Feedback)
api_key = os.getenv("GEMINI_API_KEY") #변수명으로 값꺼냄

client = genai.Client(api_key=api_key)

# 왜 밖에 두는 게 맞냐 다시 짚자면: 키 읽기랑 점원 부르기는 프로그램 켤 때 딱 한 번만 하면 돼.

def embed_feedback(prompt):
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=prompt
    
          
    )
    return response.embeddings[0].values
    

#아래만 있으면 rag_docs 있는답 그대로 나옴

with open("rag_docs/위축형_칭찬법.md", "r",encoding="utf-8") as f:
    text = f.read()
chunking= text.split("##")

chunks = []
for c in chunking[1:]:
    chunks.append(c.strip())
print(len(chunks))
print(chunks[0])

vectors = []
for c in chunks:
      vectors.append(embed_feedback(c))

print(len(vectors))       # 8   ← 벡터가 8개 만들어졌나
print(len(vectors[0]))    # 3072 ← 그중 0번은 숫자 3072개인가


data = []
for c, v in zip(chunks, vectors):
      data.append({"text": c, "vector": v})

with open("Kids_Feedback/rag/vectors.json", "w", encoding="utf-8") as f:
      json.dump(data, f, ensure_ascii=False)

print("저장 완료:", len(data))


