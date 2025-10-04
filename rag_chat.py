# rag_chat.py
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# ===============================
# ✅ 모델 및 인덱스 초기화
# ===============================
EMBED_MODEL_ID = "BAAI/bge-small-en-v1.5"
LLM_ID = "EleutherAI/polyglot-ko-1.3b"

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

# ===============================
# ✅ RAG 답변 함수
# ===============================
def rag_answer(query, persona="default", top_k=3):
    # 1️⃣ 유사 문서 검색
    q_emb = embed_model.encode([query], normalize_embeddings=True)
    q_emb = np.array(q_emb, dtype="float32")
    D, I = index.search(q_emb, k=top_k)
    hits = [documents[idx] for idx in I[0]]

    # 2️⃣ 페르소나별 톤 설정
    if persona == "doctor":
        tone = "의사처럼 전문적이고 신중한 말투로 답변하세요. 의학적 표현을 사용하되 이해하기 쉽게 설명하세요."
    elif persona == "herbalist":
        tone = "한의사처럼 따뜻하고 자연 친화적인 말투로 답변하세요. 기혈, 음양, 체질 등의 개념을 적절히 활용하세요."
    elif persona == "trainer":
        tone = "헬스 트레이너처럼 활기차고 동기부여되는 말투로 답변하세요. 긍정적이고 에너지 넘치게 말하세요."
    else:
        tone = "친절하고 명확한 말투로 답변하세요."

    # 3️⃣ 프롬프트 구성
    context = "\n".join([f"- {doc}" for doc in hits])
    prompt = f"""당신은 {tone}

사용자 질문:
{query}

참고할 수 있는 컨텍스트:
{context}

위 정보를 바탕으로, 사용자에게 도움이 되는 답변을 작성하세요.
최종 답변:"""

    # 4️⃣ LLM 호출
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    if "token_type_ids" in inputs:
        del inputs["token_type_ids"]

    outputs = model.generate(
        **inputs,
        max_new_tokens=100,
        no_repeat_ngram_size=3,
        temperature=0.7,
        top_p=0.9
    )

    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # 5️⃣ 원본 출력 로그
    print("\n=== RAW MODEL OUTPUT ===")
    print(answer)
    print("========================\n")

    # 6️⃣ 결과 정제
    if "최종 답변:" in answer:
        answer = answer.split("최종 답변:")[-1].strip()

    return hits, answer
