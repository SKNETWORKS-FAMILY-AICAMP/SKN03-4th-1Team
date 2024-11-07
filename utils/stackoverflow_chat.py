from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from .search_stackoverflow import search_similar_questions
from typing import List, Dict, Tuple

def create_stackoverflow_chat():
    """StackOverflow 검색 결과를 활용하는 챗봇 체인 생성"""
    
    template = """당신은 프로그래밍 전문가입니다. 
    아래의 StackOverflow 검색 결과를 참고하여 사용자의 질문에 한국어로 답변해주세요.
    
    검색된 StackOverflow 결과:
    {stackoverflow_results}
    
    사용자 질문: {user_question}
    
    답변 형식:
    1. 핵심 답변을 한국어로 간단히 제시
    2. 필요한 경우 코드 예시 제공
    3. 상세 설명과 주의사항
    4. 참고한 StackOverflow 링크 (반드시 위의 검색 결과에 있는 링크만 사용할 것)
    
    답변:"""

    prompt = ChatPromptTemplate.from_template(template)
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7
    )
    
    return LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True
    )

def format_stackoverflow_results(results):
    """StackOverflow 검색 결과를 포맷팅"""
    formatted_text = "\nStackOverflow 검색 결과:"
    
    for idx, result in enumerate(results, 1):
        try:
            title = result.get('Title', 'No title available')
            answer = result.get('Answer Chunks', 'No answer available')
            link = result.get('Link', '')
            
            formatted_text += f"\n{idx}. Question: {title}\n"
            formatted_text += f"Answer: {answer}\n"
            formatted_text += f"Reference: {link}\n"
            formatted_text += "-" * 50 + "\n"
            
        except Exception as e:
            print(f"Error formatting result {idx}: {e}")
            continue
    
    return formatted_text

def get_stackoverflow_response(query: str) -> Tuple[str, List[Dict]]:
    """StackOverflow 검색 결과와 AI 응답을 반환"""
    
    # StackOverflow 검색 실행
    search_results = search_similar_questions(
        query=query,
        top_k=3
    )
    
    # 검색 결과가 없는 경우를 처리
    if not search_results:
        return "검색 결과가 없습니다.", []
    
    # 검색 결과 포맷팅
    formatted_results = format_stackoverflow_results(search_results)
    
    # LLM 체인 생성
    chain = create_stackoverflow_chat()
    
    try:
        # 답변 생성
        response = chain.invoke({
            "stackoverflow_results": formatted_results,
            "user_question": query
        })
        
        return response["text"], search_results  # search_results를 반환하도록 수정
    except Exception as e:
        print(f"Error generating response: {e}")
        return "답변 생성 중 오류가 발생했습니다.", search_results
