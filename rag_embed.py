# rag_embed.py
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle

# 1. CSV 불러오기
df = pd.read_csv("disease_region_filtered.csv")
print("👉 CSV 불러오기 완료")

# 2. 텍스트로 변환
documents = df.apply(
    lambda row: f"{row['year']} {row['sidoNm']} {row['icdNm']} 발생 건수 {row['resultVal']}건",
    axis=1
).tolist()
print("👉 텍스트 변환 완료, 문서 개수:", len(documents))

# 3. 임베딩 생성
embed_model = SentenceTransformer("BAAI/bge-small-en-v1.5")
embeddings = embed_model.encode(
    documents,
    batch_size=16,
    normalize_embeddings=True,
    show_progress_bar=True
)
print("👉 임베딩 완료, shape:", embeddings.shape)

# 4. FAISS 인덱스 생성
dim = embeddings.shape[1]
index = faiss.IndexFlatL2(dim)
index.add(np.array(embeddings, dtype="float32"))
print("✅ FAISS에 데이터 저장 완료!")

# 5. 인덱스와 문서 저장 (pickle + faiss)
faiss.write_index(index, "faiss.index")
with open("documents.pkl", "wb") as f:
    pickle.dump(documents, f)

print("✅ faiss.index + documents.pkl 저장 완료")

# 6. 임베딩 검증 (테스트 검색)
query = "서울 에볼라바이러스병 발생 건수"
query_emb = embed_model.encode([query], normalize_embeddings=True)

D, I = index.search(np.array(query_emb, dtype="float32"), k=5)
print("\n🔍 임베딩 검증 테스트")
print("테스트 쿼리:", query)
for rank, idx in enumerate(I[0]):
    print(f"{rank+1}위 | {documents[idx]} (score={D[0][rank]:.4f})")
