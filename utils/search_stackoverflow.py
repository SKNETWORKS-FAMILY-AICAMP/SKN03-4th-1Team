from dotenv import load_dotenv
import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from deep_translator import GoogleTranslator
from typing import List, Dict
from sentence_transformers import CrossEncoder

# .env 파일 로드 및 확인
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def search_similar_questions(query: str, top_k: int = 5) -> List[Dict]:
    """StackOverflow 질문 검색"""
    try:
        # 리랭커 초기화
        cross_encoder = CrossEncoder("Dongjin-kr/ko-reranker", max_length=512, device="cpu")
        
        # 한국어 쿼리를 영어로 번역
        translator = GoogleTranslator(source='ko', target='en')
        translated_query = translator.translate(query)
        
        # 임베딩 모델 초기화
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
        # 벡터스토어 로드
        vectorstore = FAISS.load_local(
            folder_path='data/c++_faiss_db',
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )
        
        # 더 많은 초기 결과 검색
        retriever = vectorstore.as_retriever(
            search_kwargs={"k": 15}  
        )
        
        initial_results = retriever.invoke(translated_query)
        
        # 리랭킹을 위한 페어 생성
        pairs = [(query, doc.page_content) for doc in initial_results]
        
        # 리랭킹 스코어 계산
        scores = cross_encoder.predict(pairs)
        
        # 결과와 스코어 결합 후 정렬
        scored_results = list(zip(initial_results, scores))
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
        # 상위 k개 결과만 선택
        results = [item[0] for item in scored_results[:top_k]]
        
        # 결과 포맷팅
        formatted_results = []
        for doc in results:
            content_parts = doc.page_content.split('\nAnswer: ')
            title = content_parts[0].replace('Title: ', '')
            answer = content_parts[1] if len(content_parts) > 1 else ''
            
            formatted_results.append({
                'Title': title,
                'Question ID': doc.metadata['Question ID'],
                'Link': doc.metadata['Link'],
                'Answer Chunks': answer,
                'Answer Count': doc.metadata['Answer Count'],
                'Answer Score': doc.metadata['Answer Score']
            })
            
        return formatted_results
        
    except Exception as e:
        print(f"검색 중 오류 발생: {e}")
        return []