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


scores.append(cos_sim(q_vector, d["vector"]))


question = "소심한 애가 처음으로 발표했는데 뭐라고 해줘야 하죠?"
q_vector = embed_feedback(question)
print(len(q_vector))
