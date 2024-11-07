import os
from dotenv import load_dotenv
import streamlit as st
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.agents import initialize_agent, Tool, AgentType
import re
import enum 

class CHATBOT_ROLE(enum.Enum):
    user = (enum.auto, "사용자")
    assistant = (enum.auto, "LLM 모델")

# message
class CHATBOT_MESSAGE(enum.Enum):
    role = (enum.auto, "작성자")
    content = (enum.auto, "메세지")
    
def __check_message(role:CHATBOT_ROLE, prompt:str):
    result = False
    if role not in CHATBOT_ROLE:
        result = True 
    elif not isinstance(prompt, str) and not len(prompt.strip()):
        result = True 

    return result

def create_message(role:CHATBOT_ROLE, prompt:str):
    if __check_message(role, prompt):
        return 

    return {
        CHATBOT_MESSAGE.role.name: role.name,
        CHATBOT_MESSAGE.content.name: prompt
    }


# 환경 변수 로드
load_dotenv()

# ChatOpenAI 및 임베딩 초기화
def initialize_llm_and_embeddings():
    llm = ChatOpenAI(model="gpt-4o-mini")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")  # 다국어 임베딩 모델 사용
    return llm, embeddings

# 벡터 DB를 로드하고 검색기 초기화
def initialize_vector_db(embeddings):
    db = FAISS.load_local(
        folder_path="data/sql_faiss_db",
        index_name="faiss_index",
        embeddings=embeddings,
        allow_dangerous_deserialization=True,
    )
    return db.as_retriever()

# 도구 정의 및 에이전트 초기화
def initialize_agent_with_tools(llm, retriever):
    tools = [
        Tool(
            name="Retriever",
            func=retriever.invoke,
            description="벡터 DB에서 질문에 대한 관련 정보를 검색합니다."
        ),
        Tool(
            name="Example Answer Provider",
            func=lambda query: llm.generate([f"SQL 질문: {query}. 관련 데이터: {retriever.invoke(query)}. 예시 답변을 제공해주세요."]).generations[0][0].text.strip(),
            description="당신은 SQL 전문가입니다. 질문에 대한 예시 답변을 한국어로 생성합니다."
        )
    ]
    
    return initialize_agent(
        tools=tools,
        llm=llm,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )



# 유사 질문 표시 (한 번에 출력)
def display_similar_questions(retriever, user_query, similar_questions):
    # 유사 질문 중 최대 3개만 출력
    similar_questions_data = []

    for question in similar_questions[:3]:
        # SQL 코드 부분만 추출하여 표시
        question_answer = question.page_content
        question_answer = re.sub(r"\[SQL_CODE_START\](.*?)\[SQL_CODE_END\]", r"```sql\n\1\n```", question_answer, flags=re.DOTALL)
        
        similar_questions_data.append({
            "title": question.metadata['title'],
            "answer": question_answer
        })

    return similar_questions_data



# 사용자 입력 처리 및 에이전트 응답 생성
def handle_user_input(page_name, agent, retriever, llm):
    chat_key = get_chat_key(page_name)
    
    user_query = st.chat_input("SQL과 관련된 질문을 입력하세요.")
    if user_query:
        # 사용자 메시지 생성
        message = create_message(role=CHATBOT_ROLE.user, prompt=user_query)
        
        # 페이지별로 메시지 저장
        if chat_key not in st.session_state:
            st.session_state[chat_key] = []
        st.session_state[chat_key].append(message)

        # 사용자 입력을 화면에 출력
        with st.chat_message(CHATBOT_ROLE.user.name):
            st.write(user_query)

        # 대화 히스토리를 포함하여 에이전트에 전달
        conversation_history = "\n".join(
            [f"{msg[CHATBOT_MESSAGE.role.name]}: {msg[CHATBOT_MESSAGE.content.name]}" for msg in st.session_state[chat_key]]
        )

        # 에이전트를 사용하여 응답 생성
        with st.chat_message(CHATBOT_ROLE.assistant.name):
            response = agent.run(f"대화 히스토리:\n{conversation_history}\n\n사용자 질문: {user_query}")
            st.markdown(response)

        # 응답 메시지를 메시지 히스토리에 추가
        st.session_state[chat_key].append(
            create_message(role=CHATBOT_ROLE.assistant, prompt=response)
        )

        # 벡터 DB에서 유사 질문 검색 한 번만 호출
        similar_questions = retriever.invoke(user_query)

        # 유사 질문과 답변을 한 번에 출력
        similar_questions_data = display_similar_questions(retriever, user_query, similar_questions)

        # 유사 질문 출력
        if similar_questions_data:
            st.subheader("유사한 StackOverflow 질문들:")
            for i, data in enumerate(similar_questions_data):
                # 질문 제목을 강조하고, 답변을 명확히 구분하여 표시
                with st.expander(f"**{i+1}. {data['title']}**"):
                    st.markdown(f"**답변:**")
                    st.write(data['answer'])
                    st.write("---")


# 대화 메시지를 페이지별로 저장
def get_chat_key(page_name):
    return f"messages_{page_name}"

# 대화 메시지를 화면에 표시
def display_chat_messages(page_name):
    chat_key = get_chat_key(page_name)
    if chat_key in st.session_state:
        for message in st.session_state[chat_key]:
            if message[CHATBOT_MESSAGE.role.name] in CHATBOT_ROLE.__members__:
                with st.chat_message(message[CHATBOT_MESSAGE.role.name]):
                    st.markdown(message[CHATBOT_MESSAGE.content.name])

# 메인 함수에서 페이지 이름을 사용
def main():
    page_name = "sql_chat_page"  # 페이지별로 고유한 이름을 사용
    st.title("Stack Overflow⚡")
    st.header("SQL Q&A Chat Bot")

    llm, embeddings = initialize_llm_and_embeddings()
    retriever = initialize_vector_db(embeddings)
    agent = initialize_agent_with_tools(llm, retriever)

    # 대화 메시지 표시
    display_chat_messages(page_name)

    # 사용자 입력 처리
    handle_user_input(page_name, agent, retriever, llm)

if __name__ == "__main__":
    main()
