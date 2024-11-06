import streamlit as st
from utils.stackoverflow_chat import get_stackoverflow_response

def main():
    st.title("StackOverflow C++ Q&A챗봇")
    
    # 세션 상태 초기화
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # 사용자 입력 (on_change 파라미터 제거)
    user_question = st.text_input("프로그래밍 관련 질문을 입력하세요:", key="user_input")
    
    # 엔터키 입력 확인
    if user_question:
        with st.spinner("답변을 생성하는 중..."):
            # 답변 생성
            response, stackoverflow_results = get_stackoverflow_response(user_question)
            
            # 채팅 기록에 추가
            st.session_state.chat_history.append({
                "question": user_question,
                "answer": response,
                "references": stackoverflow_results
            })
    
    # 채팅 기록 표시
    for chat in reversed(st.session_state.chat_history):
        with st.container():
            st.write("---")
            st.write("👤 **질문:**")
            st.write(chat["question"])
            st.write("🤖 **답변:**")
            st.write(chat["answer"])
            
            # stackoverflow 결과가 있는 경우에만 표시
            references = chat.get("references", [])
            if references:
                st.write("### 참고한 StackOverflow 글:")
                for ref in references:
                    st.write(f"""
                    - **제목**: {ref['Title']}
                    - **답변**: {ref['Answer Chunks']}
                    - **링크**: {ref['Link']}
                    ---
                    """)

if __name__ == "__main__":
    main() 