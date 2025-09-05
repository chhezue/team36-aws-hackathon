"""
감성 분석용 외부 리소스 관리
"""
import os
import requests
from pathlib import Path

class SentimentResourceManager:
    def __init__(self):
        self.resource_dir = Path(__file__).parent / 'resources'
        self.resource_dir.mkdir(exist_ok=True)
    
    def download_korean_stopwords(self):
        """한국어 불용어 사전 다운로드"""
        url = "https://raw.githubusercontent.com/stopwords-iso/stopwords-ko/master/stopwords-ko.txt"
        file_path = self.resource_dir / 'korean_stopwords.txt'
        
        if not file_path.exists():
            try:
                response = requests.get(url)
                response.raise_for_status()
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"한국어 불용어 사전 다운로드 완료: {file_path}")
            except Exception as e:
                print(f"불용어 사전 다운로드 실패: {e}")
                return self._get_default_stopwords()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return set(word.strip() for word in f.readlines() if word.strip())
    
    def load_sentiment_dictionary(self):
        """감성 사전 로드 (KNU 한국어 감성사전 기반)"""
        positive_file = self.resource_dir / 'positive_words.txt'
        negative_file = self.resource_dir / 'negative_words.txt'
        
        # 기본 감성 사전 생성 (실제로는 KNU 감성사전 등 활용)
        if not positive_file.exists():
            self._create_default_sentiment_dict()
        
        positive_words = self._load_word_file(positive_file)
        negative_words = self._load_word_file(negative_file)
        
        return positive_words, negative_words
    
    def _create_default_sentiment_dict(self):
        """기본 감성 사전 생성"""
        positive_words = [
            # 일반 긍정어
            '좋다', '훌륭하다', '만족', '추천', '최고', '완벽', '우수', '뛰어나다',
            '성공', '발전', '개선', '향상', '효과적', '유용', '도움', '편리',
            
            # 지역 특화 긍정어
            '맛있다', '깨끗하다', '친절하다', '안전하다', '조용하다', '편안하다',
            '축제', '행사', '이벤트', '할인', '무료', '개방', '신규', '새로',
            '오픈', '개업', '완성', '개통', '확정', '승인', '지원', '혜택',
            
            # 감정 표현
            '기쁘다', '즐겁다', '행복하다', '감사하다', '고맙다', '반갑다'
        ]
        
        negative_words = [
            # 일반 부정어
            '나쁘다', '불만', '실망', '문제', '어려움', '힘들다', '복잡하다',
            '불편', '위험하다', '무서워', '걱정', '불안', '스트레스',
            
            # 지역 특화 부정어
            '사고', '화재', '범죄', '도난', '소음', '악취', '더럽다', '지저분',
            '폐쇄', '중단', '지연', '취소', '철거', '공사', '막히다', '혼잡',
            '반대', '항의', '민원', '불법', '위반', '처벌', '단속', '벌금',
            
            # 감정 표현
            '화나다', '짜증', '속상하다', '우울하다', '슬프다', '답답하다'
        ]
        
        # 파일로 저장
        self._save_word_file(self.resource_dir / 'positive_words.txt', positive_words)
        self._save_word_file(self.resource_dir / 'negative_words.txt', negative_words)
    
    def _load_word_file(self, file_path):
        """단어 파일 로드"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return [word.strip() for word in f.readlines() if word.strip()]
    
    def _save_word_file(self, file_path, words):
        """단어 파일 저장"""
        with open(file_path, 'w', encoding='utf-8') as f:
            for word in words:
                f.write(f"{word}\n")
    
    def _get_default_stopwords(self):
        """기본 불용어 반환"""
        return {
            '이', '가', '을', '를', '에', '의', '와', '과', '도', '로', '으로',
            '은', '는', '이다', '있다', '없다', '하다', '되다', '것', '수', '등',
            '그', '저', '이것', '그것', '저것', '여기', '거기', '저기',
            '때', '곳', '데', '말', '사람', '년', '월', '일', '시간'
        }