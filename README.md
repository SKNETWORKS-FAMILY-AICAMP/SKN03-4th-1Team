# SKN03-4th-1Team

**팀명 : 일주일**

## 😀팀원

- 박중헌
- 박용주
- 이준석
- 송영빈
- 이준경
- 김병수

# ✨Stackoverflow-QA-Finder

## 📌개요

**Stackoverflow-QA-Finder**는 스택 오버플로우의 질문과 답변을 쉽게 찾고 필터링할 수 있도록 도와주는 시스템입니다.

사용자가 필요한 영어로 된 질문을 한국어로 번역하고 관련된 기존 질문과 답변을 자동으로 검색 및 요약하여 쉽게 접근할 수 있도록 합니다.

이 프로젝트는 **Langchain**과 **OpenAI**를 사용한 **RAG** 방식을 활용하여 실시간 답변을 제공합니다.

## 📌파이프라인

<details>
  <summary> SQL</summary>

### 1. 데이터 수집

- **StackOverflow 질문과 답변 수집**

  - StackExchange API를 사용하여 질문과 답변 데이터 수집

- **데이터 전처리**

  - SQL 코드는 보존하면서 HTML 태그 제거

- **임베딩 및 Vector Database 생성**
  - 임베딩 모델 및 FAISS를 사용하여 vectorDB 생성

### 2. 초기화 단계

- **임베딩 및 LLM 설정**:
  - OpenAI 모델 (`gpt-4o-mini`)과 텍스트 임베딩 모델 (`text-embedding-3-small`)을 초기화
- **벡터 DB 로드**:

  - **FAISS 벡터 데이터베이스**를 로드하여 SQL 관련 질문을 벡터화하고, 유사 질문 검색 기능을 설정

- **에이전트 초기화**:
  - LangChain 에이전트를 사용하여 **검색기**와 **생성 모델**을 통합
  - `Retriever`: 벡터 DB에서 질문에 대한 관련 정보 검색
  - `Example Answer Provider`: SQL 질문에 대한 예시 답변 생성

### 3. 대화 관리

- **대화 히스토리 저장**:
  - 사용자의 질문과 챗봇의 응답을 **세션에 저장**하여 대화 히스토리 유지

### 4. 질문 처리 및 응답 생성

- **유사 질문 검색**:

  - 사용자의 질문을 벡터화하여 **벡터 DB**에서 유사한 질문을 검색

- **응답 생성**:
  - 생성 모델이 검색된 유사 질문 결과와 대화 히스토리를 기반으로 답변 생성

### 5. 유사 질문 표시

- **답변과 유사한 질문 출력**</details>

<details>
  <summary>C++</summary>
  
### 1. Stack Overflow 데이터 수집
   - Stack Overflow의 질문과 답변을 수집하여 챗봇 학습에 필요한 데이터를 확보
      - Stack Overflow API를 사용하여 질문과 답변 데이터 수집
      - 각 질문의 태그, 질문 내용, 답변 등을 포함한 JSON 형식으로 데이터를 저장
      - 채택된 답변만 수집

### 2. 데이터 전처리

- 텍스트 전처리: 불필요한 특수문자 제거, 소문자 변환, HTML 태그 제거 등의 전처리

### 3. 임베딩 및 청킹

- 질문과 답변을 벡터화하여 유사 질문 검색에 사용할 벡터 DB를 생성하고, 긴 문장을 효율적으로 처리하기 위해 답변만 청킹 (질문은 거의 다 짧음)
  - **청킹**: 긴 텍스트는 일정한 길이의 청크로 나눠서 처리
  - **임베딩**: 각 청크를 임베딩(벡터)으로 변환하기 위해 OPENAI text-embedding-3-small 모델 사용
  - **벡터 저장**: 청킹과 임베딩을 거친 벡터들을 FAISS에 저장

### 4. Retriever 구축

- 챗봇에 입력한 질문과 유사한 질문을 벡터 DB에서 검색하여 답변 반환 (한글로)
  - 사용자의 질문을 GoogleTranslator로 영어로 번역 후 임베딩을 통해 **유사도**가 가장 높은 질문 벡터 검색

### 5. Reranker 설정

- 크로스 인코더를 사용해 검색된 답변 후보 중 가장 적절한 답변을 재정렬하여 최적의 답변을 선택

### 6. LLM을 사용한 답변 요약 및 참고 자료 제공

- 프롬프트를 스택오버플로우에 맞게 작성 - LLM을 통해 이해하기 쉬운 형태로 답변을 요약 - 관련 질문이나 참고 자료 링크를 추가
   
## 실행 화면
![c_1](https://github.com/user-attachments/assets/b6f0a205-e218-4026-beaf-9ad4cc3ef982)
![c_2](https://github.com/user-attachments/assets/278a3eb2-d8fc-405e-84b3-92245e199081)
![c_3](https://github.com/user-attachments/assets/8a31f2d0-403b-4701-b463-48bf545dc192)

</details>

<details>
  <summary>Python</summary>

</details>

<details>
  <summary>C#</summary>

</details>

<details>
  <summary>Javascript</summary>

</details>

<details>
  <summary>Java</summary>

</details>

###

## 📌기술스택

| ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) | ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=whit) |![Langchain](https://img.shields.io/badge/Langchain-00C7B7?logo=langchain&logoColor=white) | ![OpenAI](https://img.shields.io/badge/OpenAI-343541?logo=openai&logoColor=white) |
