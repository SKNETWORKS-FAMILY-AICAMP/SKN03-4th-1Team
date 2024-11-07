import pandas as pd
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from html import unescape
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
import pickle

load_dotenv()

def preprocess_data(tag='c++'):
    # CSV 파일에서 데이터 로드
    df = pd.read_csv('data/stackoverflow_questions.csv')
    print(f"총 질문 수: {len(df)}")
    
    processed_data = []
    
    def preprocess_text(text):
        # NaN 값이나 빈 값 처리
        if pd.isna(text) or not text:
            return None
        
        # 문자열로 변환
        text = str(text)
        
        soup = BeautifulSoup(text, 'html.parser')
        
        code_blocks = []
        for code in soup.find_all('code'):
            code_blocks.append(code.get_text())
            code.replace_with('[CODE]')
        
        text = soup.get_text()
        text = unescape(text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        for _, code in enumerate(code_blocks):
            text = text.replace('[CODE]', f'\n```\n{code}\n```\n', 1)
        
        return text
    
    for _, row in df.iterrows():
        processed_item = {
            'Question ID': row['Question ID'],
            'Title': preprocess_text(row['Title']),
            'Link': row['Link'],
            'Answer Count': row['Answer Count'],
            'Accepted Answer Score': row['Accepted Answer Score'],
            'Accepted Answer Body': preprocess_text(row['Accepted Answer Body'])
        }
        processed_data.append(processed_item)
    
    # 전처리된 데이터 저장
    with open(f'data/stackoverflow_{tag}_processed_data.pkl', 'wb') as f:
        pickle.dump(processed_data, f)
    
    return processed_data

def process_embeddings(tag='c++'):
    # 전처리된 데이터 로드
    with open(f'data/stackoverflow_{tag}_processed_data.pkl', 'rb') as f:
        processed_data = pickle.load(f)
    
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # 텍스트 스플리터 초기화
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    # Document 객체 리스트 생성
    documents = []
    for item in processed_data:
        if item['Title'] and item['Accepted Answer Body']:
            combined_text = f"Title: {item['Title']}\nAnswer: {item['Accepted Answer Body']}"
            metadata = {
                'Question ID': item['Question ID'],
                'Link': item['Link'],
                'Answer Count': item['Answer Count'],
                'Answer Score': item['Accepted Answer Score'],
                'Accepted Answer Body': item['Accepted Answer Body']
            }
            # 텍스트를 청크로 분할
            chunks = text_splitter.split_text(combined_text)
            for chunk in chunks:
                documents.append(Document(page_content=chunk, metadata=metadata))
    
    # FAISS 벡터스토어 생성
    vectorstore = FAISS.from_documents(documents=documents, embedding=embeddings)
    
    # 벡터스토어 저장
    vectorstore.save_local(f'data/c++_faiss_db')
    
    return documents

# 메인 실행 코드 수정
if __name__ == "__main__":
    tag = 'c++'
    
    # 2. 데이터 전처리
    processed_data = preprocess_data(tag=tag)
    print("데이터 전처리 완료")
    
    # 3. 임베딩 및 청킹 처리
    final_data = process_embeddings(tag=tag)
    print("임베딩 및 청킹 처리 완료")