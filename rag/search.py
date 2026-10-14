import json
import os
from dotenv import load_dotenv
from google import genai
import math
with open("Kids_Feedback/rag/vectors.json", "r", encoding="utf-8") as f:
      data = json.load(f)

print(len(data))
print(data[0]["text"][:40])

load_dotenv("Kids_Feedback/.env")
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


def generate_feedback(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={"response_mime_type": "application/json"},  # ```json 없이 순수 JSON만 받기
    )
    return response.text



def embed_feedback(prompt):
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=prompt
      )
    return response.embeddings[0].values



def cos_sim(a, b):
      dot = sum(x * y for x, y in zip(a, b))
      size_a = math.sqrt(sum(x * x for x in a))
      size_b = math.sqrt(sum(x * x for x in b))
      return dot / (size_a * size_b)

def rag_search(question):      # for 밖, 1번만
      q_vector = embed_feedback(question)  # for 밖, 1번만
      scores= []
      for d in data:
            scores.append(cos_sim(q_vector, d["vector"]))
      best = scores.index(max(scores))
      found = data[best]["text"]
      return found

question = "소심한 애가 처음으로 발표했는데 뭐라고 해줘야 하죠?"   # 질문 준비
found = rag_search(question)     


prompt = f"""너는 아이 줄넘기 수업 강사를 돕는 AI야.
아래 [지도 가이드]를 근거로, [상황]에 맞는 피드백을 짧게 써줘.

[지도 가이드]
{found}
g
[상황]
{question}
"""

answer = generate_feedback(prompt)
print(answer)
