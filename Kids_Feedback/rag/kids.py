#  임포트 걱정 없으니 바로 가자. rag_docs/위축형_칭찬법.md 읽어서 .split("##") 한 다음 print로
#   찍어봐. 쳐와!

with open("rag_docs/위축형_칭찬법.md", "r",encoding="utf-8") as f:
    text = f.read()
chunking= text.split("##")
print(chunking)
