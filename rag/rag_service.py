import json
import os
import math
from pathlib import Path

from dotenv import load_dotenv
from google import genai

BASE_DIR = Path(__file__).resolve().parent.parent

with open(BASE_DIR / "rag" / "vectors.json", "r", encoding="utf-8") as f:
    data = json.load(f)

load_dotenv(BASE_DIR / ".env")
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




def rag_search(question):      # for 밖, 1번만
      q_vector = embed_feedback(question)  # for 밖, 1번만
      scores= []
      for d in data:
            scores.append(cos_sim(q_vector, d["vector"]))
      best = scores.index(max(scores))
      found = data[best]["text"]
      return found