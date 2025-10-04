Mini RAG Chatbot
1. 사용한 모델

원래 계획: Llama-3.2-3B-Instruct

실제 사용: EleutherAI/polyglot-ko-1.3b

이유: 로컬 환경에서 실행하기 위해 비교적 가벼운 한국어 지원 모델을 사용함.

NPU에 올릴 때는 LLaMA 모델로 교체 가능.


2. 실행 방법

FAISS 인덱스 & 문서 파일 필요: faiss.index, documents.pkl

없으면 rag_embed.py 실행해서 생성

서버 실행:

python rag_server.py


프론트엔드 실행 (React UI):

cd ui
npm start


브라우저에서 http://localhost:3000 접속 후 질문 입력



3. 현재 답변 품질의 한계

예시:

최종 답변: 에볼라는 에볼라바이러스가 아닙니다. 에볼라도 에볼라바이러스입니다. 
에볼라바이러스는 에볼라바이러스의 변종입니다. 
에볼라바이러스는 바이러스가 아닙니다, 바이러스는 숙주에 기생하는 기생충입니다.

원인

모델 한계

Polyglot-ko-1.3b는 기본 GPT-style LM으로 instruction tuning이 약함

"최종 답변:" 지시문을 무시하거나 문장을 반복 생성

프롬프트 설계 부족

"짧고 간결하게" 같은 제약이 없어 장황하거나 모순된 답변 발생

지식 검증 부재

LLM의 생성 결과를 그대로 출력 → 사실 오류 발생



4. 개선 방향

프롬프트 강화

당신은 한국어 의료 데이터 요약 어시스턴트입니다. 
아래 컨텍스트를 근거로 짧고 간단히 답하세요. 
컨텍스트에 없는 내용은 '정보 없음'이라고만 답하세요.


후처리 제약

max_new_tokens 줄여서 불필요한 반복 방지

no_repeat_ngram_size 옵션으로 문장 반복 최소화

더 나은 모델 사용

instruction tuning된 한국어 모델: snunlp/KR-Llama-1.3B-v1.0

실제 NPU 환경에서는 LLaMA 기반 instruct 모델 사용 예정
