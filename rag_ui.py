# rag_ui.py
import gradio as gr
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

EMBED_MODEL_ID = "BAAI/bge-small-en-v1.5"
LLM_ID = "meta-llama/Llama-3.2-3B-Instruct"

# 인덱스/문서 불러오기
index = faiss.read_index("faiss.index")
with open("documents.pkl", "rb") as f:
    documents = pickle.load(f)

embed_model = SentenceTransformer(EMBED_MODEL_ID)

tokenizer = AutoTokenizer.from_pretrained(LLM_ID)
model = AutoModelForCausalLM.from_pretrained(
    LLM_ID,
    device_map="auto",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
)

def rag_chat(query):
    q_emb = embed_model.encode([query], normalize_embeddings=True)
    q_emb = np.array(q_emb, dtype="float32")
    D, I = index.search(q_emb, k=3)
    hits = [documents[idx] for idx in I[0]]

    context = "\n".join([f"- {doc}" for doc in hits])
    prompt = f"""질문: {query}

컨텍스트:
{context}

답변:"""

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=300)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    if "답변:" in answer:
        answer = answer.split("답변:")[-1].strip()

    return answer

demo = gr.Interface(
    fn=rag_chat,
    inputs=gr.Textbox(label="질문 입력"),
    outputs=gr.Textbox(label="답변"),
    title="미니 RAG 챗봇",
    description="FAISS 검색 결과를 기반으로 Llama-3.2-3B-Instruct가 답변합니다."
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
