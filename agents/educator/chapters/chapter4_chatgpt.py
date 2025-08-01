# agents/educator/chapters/chapter4_chatgpt.py
# 챕터 4: ChatGPT로 할 수 있는 것들 콘텐츠 생성

from typing import Dict, List, Any
from .base_chapter import BaseChapter


class Chapter4ChatGPT(BaseChapter):
    """챕터 4: ChatGPT로 할 수 있는 것들 콘텐츠 생성 클래스"""
    
    def __init__(self):
        super().__init__()
        self.chapter_id = 4
        self.title = 'ChatGPT로 할 수 있는 것들'
        self.objectives = [
            'ChatGPT의 주요 활용 분야와 기능 이해',
            '요약, 번역, 질문 생성 등 실용적 기능 체험',
            '업무 효율성 향상을 위한 ChatGPT 활용법 학습'
        ]
        self.key_concepts = [
            '텍스트 생성', '요약', '번역', '질문 생성', '코드 작성', '창작', '분석'
        ]
        self.examples = {
            'beginner': [
                '긴 글 요약하기: "이 기사를 3줄로 요약해줘"',
                '언어 번역하기: "이 문장을 영어로 번역해줘"',
                '아이디어 생성하기: "여행 계획 아이디어 10개 알려줘"'
            ],
            'business': [
                '회의록 요약 및 액션 아이템 추출',
                '마케팅 카피 및 제안서 초안 작성',
                '데이터 분석 결과 해석 및 보고서 생성'
            ]
        }
    
    def get_chapter_template(self) -> Dict[str, Any]:
        """챕터 4 템플릿 반환"""
        return {
            'title': self.title,
            'objectives': self.objectives,
            'key_concepts': self.key_concepts,
            'examples': self.examples
        }
    
    def generate_section_title(self, objective: str, user_level: str) -> str:
        """섹션 제목 생성"""
        if user_level == 'low':
            # 친근한 제목
            title_map = {
                'ChatGPT의 주요 활용 분야와 기능 이해': '🚀 ChatGPT 활용법',
                '요약, 번역, 질문 생성 등 실용적 기능 체험': '⚡ 실용적 기능들',
                '업무 효율성 향상을 위한 ChatGPT 활용법 학습': '💼 업무에 활용하기'
            }
        else:
            # 전문적인 제목
            title_map = {
                'ChatGPT의 주요 활용 분야와 기능 이해': 'ChatGPT 기능 및 활용 분야',
                '요약, 번역, 질문 생성 등 실용적 기능 체험': '핵심 기능별 활용 전략',
                '업무 효율성 향상을 위한 ChatGPT 활용법 학습': '비즈니스 프로세스 최적화'
            }
        
        return title_map.get(objective, objective)
    
    def generate_section_content(self, objective: str, key_concepts: List[str], 
                                user_type: str, user_level: str) -> str:
        """섹션별 콘텐츠 생성"""
        
        if 'ChatGPT' in objective and '활용 분야' in objective:
            return self._generate_chatgpt_overview_content(user_level)
        elif '요약' in objective or '번역' in objective or '실용적' in objective:
            return self._generate_practical_functions_content(user_level)
        elif '업무 효율성' in objective or '비즈니스' in objective:
            return self._generate_business_applications_content(user_level)
        else:
            return f"{objective}에 대한 상세한 설명이 여기에 들어갑니다."
    
    def _generate_chatgpt_overview_content(self, user_level: str) -> str:
        """ChatGPT 개요 콘텐츠"""
        if user_level == 'low':
            return """
ChatGPT는 정말 다양한 일을 할 수 있는 만능 AI 도우미입니다!

📝 **텍스트 작업**
- **요약하기**: 긴 글을 짧게 정리해줘요
  - "이 기사를 3줄로 요약해줘"
- **번역하기**: 다른 언어로 번역해줘요
  - "이 문장을 영어로 번역해줘"
- **글쓰기**: 이메일, 편지, 보고서 등을 써줘요
  - "감사 인사 이메일 써줘"

🤔 **아이디어 도우미**
- **질문 만들기**: 공부할 때 문제를 만들어줘요
- **아이디어 생성**: 창의적인 아이디어를 제안해줘요
- **계획 세우기**: 여행, 공부 계획을 도와줘요

💻 **실용적 활용**
- **설명하기**: 어려운 개념을 쉽게 설명
- **검토하기**: 내가 쓴 글을 확인하고 개선점 제안
- **대화하기**: 궁금한 것을 자유롭게 물어보기

🎨 **창작 활동**
- **이야기 쓰기**: 소설, 시나리오 작성
- **코드 작성**: 간단한 프로그래밍 도움
- **레시피 추천**: 요리법 제안

💡 **팁**: 구체적으로 요청할수록 더 좋은 결과를 얻을 수 있어요!
            """
        else:
            return """
ChatGPT는 다양한 비즈니스 태스크에서 생산성을 크게 향상시킬 수 있는 도구입니다.

**핵심 활용 분야**

1. **문서 작업 자동화**
   - 회의록 요약 및 액션 아이템 추출
   - 보고서 초안 작성 및 구조화
   - 이메일 템플릿 생성 및 개인화
   - 제안서 및 기획서 작성 지원

2. **콘텐츠 생성 및 편집**
   - 마케팅 카피 및 광고 문구 작성
   - 블로그 포스트 및 소셜미디어 콘텐츠
   - 프레젠테이션 스크립트 개발
   - 기술 문서 및 매뉴얼 작성

3. **데이터 분석 지원**
   - 복잡한 데이터 해석 및 인사이트 도출
   - 차트 및 그래프 설명 생성
   - 트렌드 분석 및 예측 보고서
   - 통계 결과 해석 및 시각화 지원

4. **고객 서비스 향상**
   - FAQ 자동 생성 및 업데이트
   - 고객 문의 응답 템플릿 작성
   - 다국어 고객 지원 콘텐츠 번역
   - 고객 피드백 분석 및 개선안 도출

5. **교육 및 훈련**
   - 교육 자료 및 커리큘럼 개발
   - 퀴즈 및 평가 문제 생성
   - 개인화된 학습 콘텐츠 제작
   - 직원 교육 프로그램 설계

**전략적 활용 방안**
- **워크플로우 통합**: 기존 업무 프로세스에 자연스럽게 통합
- **품질 관리**: 일관된 톤앤매너 및 브랜드 가이드라인 준수
- **효율성 측정**: ROI 및 생산성 향상 지표 추적
- **지속적 개선**: 사용자 피드백 기반 프롬프트 최적화
            """
    
    def _generate_practical_functions_content(self, user_level: str) -> str:
        """실용적 기능 콘텐츠"""
        if user_level == 'low':
            return """
ChatGPT의 실용적인 기능들을 하나씩 알아볼까요?

📄 **요약 기능**
- **긴 글 요약**: "이 기사를 3줄로 요약해줘"
- **핵심 포인트 추출**: "이 문서의 주요 내용 5가지만 알려줘"
- **회의록 정리**: "회의 내용을 요약하고 할 일 목록 만들어줘"

🌍 **번역 기능**
- **언어 번역**: "이 문장을 영어로 번역해줘"
- **자연스러운 번역**: "격식있게 번역해줘" / "친근하게 번역해줘"
- **문화적 맥락 고려**: "한국 문화에 맞게 번역해줘"

❓ **질문 생성**
- **학습용 문제**: "이 내용으로 퀴즈 5문제 만들어줘"
- **면접 질문**: "마케팅 직무 면접 질문 10개 만들어줘"
- **토론 주제**: "이 주제로 토론할 수 있는 질문들 만들어줘"

💡 **아이디어 생성**
- **브레인스토밍**: "새로운 앱 아이디어 10개 제안해줘"
- **문제 해결**: "이 문제를 해결할 방법들 알려줘"
- **창의적 제안**: "독특한 생일 파티 아이디어 추천해줘"

✍️ **글쓰기 도움**
- **초안 작성**: "감사 편지 초안 써줘"
- **문체 변경**: "이 글을 더 공식적으로 바꿔줘"
- **맞춤법 검사**: "이 글의 오타와 문법 오류 찾아줘"

🔍 **분석 및 설명**
- **개념 설명**: "블록체인을 초등학생도 이해할 수 있게 설명해줘"
- **장단점 분석**: "재택근무의 장단점을 표로 정리해줘"
- **비교 분석**: "아이폰과 갤럭시의 차이점 알려줘"
            """
        else:
            return """
ChatGPT의 핵심 기능별 전문적 활용 전략을 살펴보겠습니다.

**텍스트 요약 (Summarization)**

1. **추상적 요약 (Abstractive Summarization)**
   - 원문의 핵심 내용을 새로운 문장으로 재구성
   - 프롬프트 예시: "다음 보고서를 경영진 브리핑용으로 3단락으로 요약"
   - 활용: 경영 보고서, 연구 논문, 시장 분석 보고서

2. **추출적 요약 (Extractive Summarization)**
   - 원문에서 중요한 문장들을 선별하여 요약
   - 프롬프트 예시: "이 계약서에서 핵심 조항 5가지만 추출"
   - 활용: 법률 문서, 기술 명세서, 정책 문서

**다국어 번역 (Translation)**

1. **컨텍스트 기반 번역**
   - 문화적, 비즈니스적 맥락을 고려한 번역
   - 프롬프트 예시: "이 마케팅 문구를 미국 시장에 맞게 영어로 번역"
   - 활용: 글로벌 마케팅, 국제 계약서, 다국어 웹사이트

2. **전문 용어 번역**
   - 특정 분야의 전문 용어를 정확하게 번역
   - 프롬프트 예시: "이 의료 논문을 의학 전문가 수준으로 번역"
   - 활용: 기술 문서, 학술 논문, 전문 매뉴얼

**질문 생성 (Question Generation)**

1. **평가 문항 생성**
   - 학습 평가 및 역량 측정을 위한 문제 생성
   - 프롬프트 예시: "이 교육 자료로 객관식 10문제, 서술형 5문제 생성"
   - 활용: 교육 평가, 채용 테스트, 자격증 시험

2. **탐색적 질문 생성**
   - 깊이 있는 사고와 토론을 유도하는 질문
   - 프롬프트 예시: "이 비즈니스 케이스로 전략적 사고를 평가할 질문 생성"
   - 활용: 컨설팅, 전략 기획, 리더십 개발

**콘텐츠 분석 (Content Analysis)**

1. **감정 분석 (Sentiment Analysis)**
   - 텍스트의 감정적 톤과 의도 분석
   - 프롬프트 예시: "이 고객 리뷰들의 감정을 분석하고 개선점 도출"
   - 활용: 고객 피드백 분석, 브랜드 모니터링, 위기 관리

2. **주제 모델링 (Topic Modeling)**
   - 대량의 텍스트에서 주요 주제와 트렌드 추출
   - 프롬프트 예시: "이 설문 응답들에서 주요 관심사 5가지 추출"
   - 활용: 시장 조사, 고객 인사이트, 트렌드 분석

**품질 관리 및 최적화**
- **일관성 확보**: 브랜드 가이드라인에 맞는 톤앤매너 유지
- **정확성 검증**: 팩트 체킹 및 전문가 리뷰 프로세스
- **효율성 측정**: 작업 시간 단축 및 품질 향상 지표 추적
- **지속적 개선**: A/B 테스트를 통한 프롬프트 최적화
            """
    
    def _generate_business_applications_content(self, user_level: str) -> str:
        """비즈니스 활용 콘텐츠"""
        if user_level == 'low':
            return """
ChatGPT를 업무에서 어떻게 활용할 수 있는지 알아볼까요?

💼 **사무 업무**
- **이메일 작성**: "고객에게 사과 이메일 써줘"
- **회의록 정리**: "회의 내용을 정리하고 다음 할 일 목록 만들어줘"
- **보고서 초안**: "월간 매출 보고서 구조 만들어줘"

📊 **기획 및 분석**
- **아이디어 회의**: "신제품 아이디어 10개 제안해줘"
- **경쟁사 분석**: "우리 제품과 경쟁사 제품 비교표 만들어줘"
- **시장 조사**: "이 설문 결과를 분석해서 인사이트 찾아줘"

📈 **마케팅**
- **광고 문구**: "20대 여성을 타겟으로 한 화장품 광고 문구 써줘"
- **SNS 콘텐츠**: "인스타그램 포스팅용 캡션 10개 만들어줘"
- **블로그 글**: "우리 제품 소개 블로그 글 써줘"

🎯 **고객 서비스**
- **FAQ 작성**: "자주 묻는 질문과 답변 10개 만들어줘"
- **고객 응답**: "불만 고객에게 보낼 답변 써줘"
- **설명서 작성**: "제품 사용법을 쉽게 설명해줘"

📚 **교육 및 훈련**
- **교육 자료**: "신입사원 교육용 자료 만들어줘"
- **퀴즈 문제**: "안전 교육 퀴즈 10문제 만들어줘"
- **매뉴얼 작성**: "업무 매뉴얼을 단계별로 써줘"

⚠️ **주의사항**
- 중요한 결정은 사람이 최종 검토해야 해요
- 개인정보나 기밀 정보는 입력하지 마세요
- 결과물을 그대로 사용하지 말고 검토 후 수정하세요
            """
        else:
            return """
ChatGPT를 활용한 비즈니스 프로세스 최적화 전략을 살펴보겠습니다.

**문서 자동화 및 템플릿화**

1. **표준 문서 생성**
   - 계약서, 제안서, 보고서 템플릿 자동 생성
   - 프롬프트 예시: "IT 서비스 계약서 표준 템플릿 생성, 주요 조항 포함"
   - ROI: 문서 작성 시간 60-80% 단축

2. **개인화된 커뮤니케이션**
   - 고객별 맞춤형 이메일, 제안서 생성
   - 프롬프트 예시: "B2B 고객사별 특성을 반영한 제안서 커스터마이징"
   - 효과: 고객 응답률 25-40% 향상

**데이터 분석 및 인사이트 도출**

1. **정성적 데이터 분석**
   - 고객 피드백, 설문 응답, 인터뷰 내용 분석
   - 프롬프트 예시: "고객 인터뷰 전사본에서 주요 Pain Point 5가지 추출"
   - 활용: 제품 개발, 서비스 개선, 고객 경험 최적화

2. **트렌드 분석 및 예측**
   - 시장 동향, 경쟁사 분석, 산업 리포트 요약
   - 프롬프트 예시: "최근 3개월 업계 뉴스를 분석하여 주요 트렌드 도출"
   - 활용: 전략 기획, 투자 의사결정, 리스크 관리

**마케팅 및 세일즈 지원**

1. **콘텐츠 마케팅 자동화**
   - 블로그, 소셜미디어, 뉴스레터 콘텐츠 생성
   - 프롬프트 예시: "B2B SaaS 기업을 위한 주간 뉴스레터 콘텐츠 생성"
   - 효과: 콘텐츠 제작 비용 50-70% 절감

2. **세일즈 스크립트 최적화**
   - 고객 유형별 맞춤형 세일즈 피치 개발
   - 프롬프트 예시: "중소기업 CEO 대상 ERP 솔루션 세일즈 스크립트"
   - 결과: 전환율 15-30% 향상

**운영 효율성 개선**

1. **프로세스 문서화**
   - 업무 매뉴얼, SOP(Standard Operating Procedure) 작성
   - 프롬프트 예시: "고객 온보딩 프로세스를 단계별로 문서화"
   - 효과: 신입 교육 시간 40-60% 단축

2. **의사결정 지원**
   - 복잡한 비즈니스 상황에 대한 다각도 분석
   - 프롬프트 예시: "신규 시장 진출 시 고려사항을 SWOT 분석으로 정리"
   - 활용: 전략 회의, 투자 검토, 리스크 평가

**품질 관리 및 거버넌스**

1. **브랜드 일관성 유지**
   - 톤앤매너 가이드라인 준수 자동 검증
   - 표준 용어집 및 스타일 가이드 적용

2. **컴플라이언스 관리**
   - 법적, 규제적 요구사항 반영 문서 생성
   - 리스크 요소 사전 식별 및 대응 방안 수립

**성과 측정 및 최적화**
- **KPI 추적**: 작업 시간 단축, 품질 향상, 비용 절감 측정
- **사용자 만족도**: 내부 직원 및 고객 만족도 조사
- **지속적 개선**: 피드백 기반 프롬프트 및 워크플로우 최적화
- **교육 및 확산**: 베스트 프랙티스 공유 및 조직 전체 역량 향상
            """