# rag_server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from rag_chat import rag_answer  # ✅ RAG 함수 import

app = Flask(__name__)
CORS(app)  # React(3000) → Flask(5000) 요청 허용

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    query = data.get("query", "")
    persona = data.get("persona", "default")  # ✅ 프론트에서 전달된 페르소나 받기

    # ✅ persona도 rag_answer로 전달
    hits, answer = rag_answer(query, persona)
    return jsonify({"answer": answer, "hits": hits})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
