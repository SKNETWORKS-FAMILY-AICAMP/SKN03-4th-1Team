import requests
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

DEFAULT_MAX_PAGES = 20

def fetch_stackoverflow_data(tag='c++', max_pages=DEFAULT_MAX_PAGES):
    api_url = "https://api.stackexchange.com/2.3/questions"
    api_key = os.environ.get("STACK_API_KEY")
    questions_data = []
    
    pagesize = 100
    
    for page in range(1, max_pages + 1):
        params = {
            'order': 'desc',
            'sort': 'votes',
            'tagged': tag,
            'site': 'stackoverflow',
            'filter': '!6VvPDzQ)xHc8k',
            'key': api_key,
            'pagesize': pagesize,  
            'page': page
        }
        
        response = requests.get(api_url, params=params)
        data = response.json()
        
        # API 응답 확인
        if 'error_id' in data or 'items' not in data:
            print(f"API 오류 발생 - 지금까지 수집된 데이터로 진행합니다.")
            break
        
        questions_data.extend(data['items'])
        print(f"페이지 {page}/{max_pages} 처리 완료 (가져온 질문 수: {len(data['items'])})")
        
        # API 제한 도달하거나 더 이상 데이터가 없으면 종료
        if not data.get('has_more') or data.get('quota_remaining', 0) < 2:
            break
    
    print(f"총 {len(questions_data)}개의 질문을 가져왔습니다.")
    
    # 데이터를 DataFrame으로 변환
    processed_questions = []
    for item in questions_data:
        question = {
            'Question ID': item['question_id'],
            'Title': item.get('title', ''),
            'Link': item.get('link', ''),
            'Answer Count': item.get('answer_count', 0),
            'Accepted Answer Score': item.get('accepted_answer_score', 0) if 'accepted_answer_score' in item else 0,
            'Accepted Answer Body': item.get('accepted_answer', {}).get('body', '') if item.get('accepted_answer') else ''
        }
        processed_questions.append(question)
    
    df = pd.DataFrame(processed_questions)
    
    os.makedirs('data', exist_ok=True)
    # CSV 파일로 저장
    df.to_csv(f'data/stackoverflow_questions.csv', index=False)
    
    return questions_data

if __name__ == "__main__":
    tag = 'c++'

    questions_data = fetch_stackoverflow_data(tag=tag)
    print("데이터 가져오기 완료")