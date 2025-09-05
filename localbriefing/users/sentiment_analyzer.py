import re
from datetime import date
from django.utils import timezone
from collections import Counter
import math

try:
    from konlpy.tag import Okt
    KONLPY_AVAILABLE = True
except ImportError:
    KONLPY_AVAILABLE = False
    print("KoNLPy not installed. Using simple keyword matching.")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("scikit-learn not installed. TF-IDF features disabled.")

class SimpleSentimentAnalyzer:
    def __init__(self):
        # 외부 리소스 매니저 초기화
        from .sentiment_resources import SentimentResourceManager
        self.resource_manager = SentimentResourceManager()
        
        # 외부 리소스에서 감성 사전 로드
        try:
            self.positive_words, self.negative_words = self.resource_manager.load_sentiment_dictionary()
            self.stopwords = self.resource_manager.download_korean_stopwords()
            print(f"감성 사전 로드 완료: 긍정 {len(self.positive_words)}개, 부정 {len(self.negative_words)}개")
            print(f"불용어 사전 로드 완료: {len(self.stopwords)}개")
        except Exception as e:
            print(f"외부 리소스 로드 실패, 기본 사전 사용: {e}")
            self._load_default_dictionaries()
        
        # 중립 키워드 (기본값)
        self.neutral_words = [
            '공지', '안내', '알림', '변경', '일정', '계획', '예정', '진행'
        ]
        
        # KoNLPy 형태소 분석기 초기화 (Java 없이 실행 가능)
        try:
            if KONLPY_AVAILABLE:
                self.okt = Okt()
            else:
                self.okt = None
        except Exception as e:
            print(f"KoNLPy 초기화 실패 (Java 필요): {e}")
            self.okt = None
            KONLPY_AVAILABLE = False
    
    def _load_default_dictionaries(self):
        """기본 사전 로드 (fallback)"""
        self.positive_words = [
            '좋다', '훌륭하다', '만족', '추천', '맛있다', '깨끗하다', '친절하다', 
            '편리하다', '안전하다', '개선', '발전', '성공', '축제', '행사', '오픈',
            '신규', '새로', '완성', '개통', '확정', '승인', '지원', '혜택'
        ]
        
        self.negative_words = [
            '나쁘다', '불만', '실망', '문제', '불편', '더럽다', '위험하다', '사고',
            '화재', '범죄', '소음', '악취', '폐쇄', '중단', '지연', '취소',
            '반대', '항의', '민원', '불법', '위반', '처벌', '단속'
        ]
        
        self.stopwords = {
            '이', '가', '을', '를', '에', '의', '와', '과', '도', '로', '으로',
            '은', '는', '이다', '있다', '없다', '하다', '되다', '것', '수', '등'
        }
    
    def _extract_keywords_konlpy(self, text, top_k=5):
        """KoNLPy를 사용한 키워드 추출"""
        if not self.okt or not text:
            return []
        
        # 형태소 분석 (명사, 형용사만 추출)
        morphs = self.okt.pos(text, stem=True)
        keywords = [word for word, pos in morphs 
                   if pos in ['Noun', 'Adjective'] 
                   and len(word) > 1 
                   and word not in self.stopwords]
        
        # 빈도 기반 상위 키워드 반환
        keyword_counts = Counter(keywords)
        return [word for word, count in keyword_counts.most_common(top_k)]
    
    def analyze_text(self, text):
        """텍스트 감성 분석 (KoNLPy + 키워드 사전 조합)"""
        if not text:
            return {'sentiment': 'neutral', 'confidence': 0.0, 'keywords': []}
        
        text = text.lower()
        
        # KoNLPy 키워드 추출
        extracted_keywords = self._extract_keywords_konlpy(text)
        
        # 감성 키워드 매칭
        pos_score = 0
        neg_score = 0
        neu_score = 0
        found_keywords = []
        
        # 추출된 키워드로 감성 점수 계산
        for keyword in extracted_keywords:
            if any(pos_word in keyword for pos_word in self.positive_words):
                pos_score += 2
                found_keywords.append(keyword)
            elif any(neg_word in keyword for neg_word in self.negative_words):
                neg_score += 2
                found_keywords.append(keyword)
            elif any(neu_word in keyword for neu_word in self.neutral_words):
                neu_score += 1
                found_keywords.append(keyword)
        
        # 원본 텍스트에서도 직접 매칭 (보완)
        for word in self.positive_words:
            if word in text and word not in found_keywords:
                pos_score += 1
                found_keywords.append(word)
        
        for word in self.negative_words:
            if word in text and word not in found_keywords:
                neg_score += 1
                found_keywords.append(word)
        
        # 감성 결정
        total_score = pos_score + neg_score + neu_score
        if total_score == 0:
            return {
                'sentiment': 'neutral', 
                'confidence': 0.1, 
                'keywords': extracted_keywords[:3]  # 추출된 키워드라도 반환
            }
        
        if pos_score > neg_score:
            sentiment = 'positive'
            confidence = min(pos_score / (pos_score + neg_score + 1), 0.9)
        elif neg_score > pos_score:
            sentiment = 'negative'
            confidence = min(neg_score / (pos_score + neg_score + 1), 0.9)
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'keywords': list(set(found_keywords))[:5]  # 중복 제거 후 최대 5개
        }
    
    def calculate_sentiment_score(self, positive_count, negative_count, neutral_count):
        """감성 점수 계산 (-1.0 ~ 1.0)"""
        total = positive_count + negative_count + neutral_count
        if total == 0:
            return 0.0
        
        pos_ratio = positive_count / total
        neg_ratio = negative_count / total
        
        return (pos_ratio - neg_ratio)
    
    def extract_tfidf_keywords(self, texts, top_k=10):
        """여러 텍스트에서 TF-IDF 기반 주요 키워드 추출"""
        if not SKLEARN_AVAILABLE or not texts or len(texts) < 2:
            return []
        
        try:
            # KoNLPy로 전처리
            if self.okt:
                processed_texts = []
                for text in texts:
                    morphs = self.okt.morphs(text)
                    filtered_morphs = [word for word in morphs 
                                     if len(word) > 1 and word not in self.stopwords]
                    processed_texts.append(' '.join(filtered_morphs))
            else:
                processed_texts = texts
            
            # TF-IDF 벡터라이저
            vectorizer = TfidfVectorizer(
                max_features=100,
                ngram_range=(1, 2),
                min_df=2
            )
            
            tfidf_matrix = vectorizer.fit_transform(processed_texts)
            feature_names = vectorizer.get_feature_names_out()
            
            # 평균 TF-IDF 점수 계산
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # 상위 키워드 반환
            top_indices = mean_scores.argsort()[-top_k:][::-1]
            return [feature_names[i] for i in top_indices]
            
        except Exception as e:
            print(f"TF-IDF 키워드 추출 오류: {e}")
            return []
    
    def analyze_batch(self, texts):
        """여러 텍스트 일괄 분석"""
        results = []
        for text in texts:
            result = self.analyze_text(text)
            results.append(result)
        
        # 전체 텍스트에서 주요 키워드 추출
        tfidf_keywords = self.extract_tfidf_keywords(texts)
        
        return {
            'individual_results': results,
            'top_keywords': tfidf_keywords
        }

def update_sentiment_summary(location, target_date=None):
    """특정 지역의 감성 요약 업데이트"""
    from .models import SentimentAnalysis, SentimentSummary
    
    if target_date is None:
        target_date = date.today()
    
    # 해당 날짜의 감성 분석 데이터 집계
    analyses = SentimentAnalysis.objects.filter(
        location=location,
        analyzed_at__date=target_date
    )
    
    positive_count = analyses.filter(sentiment='positive').count()
    negative_count = analyses.filter(sentiment='negative').count()
    neutral_count = analyses.filter(sentiment='neutral').count()
    
    # 키워드 집계 및 TF-IDF 분석
    all_keywords = {'positive': [], 'negative': []}
    all_texts = {'positive': [], 'negative': []}
    
    for analysis in analyses:
        if analysis.sentiment == 'positive':
            all_keywords['positive'].extend(analysis.keywords)
        elif analysis.sentiment == 'negative':
            all_keywords['negative'].extend(analysis.keywords)
    
    # 상위 키워드 추출
    analyzer = SimpleSentimentAnalyzer()
    top_positive = [word for word, count in Counter(all_keywords['positive']).most_common(5)]
    top_negative = [word for word, count in Counter(all_keywords['negative']).most_common(5)]
    
    # 감성 점수 계산
    analyzer = SimpleSentimentAnalyzer()
    sentiment_score = analyzer.calculate_sentiment_score(
        positive_count, negative_count, neutral_count
    )
    
    # 요약 데이터 저장/업데이트
    summary, created = SentimentSummary.objects.update_or_create(
        location=location,
        date=target_date,
        defaults={
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'sentiment_score': sentiment_score,
            'top_keywords': {
                'positive': top_positive,
                'negative': top_negative
            }
        }
    )
    
    return summary