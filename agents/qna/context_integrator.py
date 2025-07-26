# agents/qna/context_integrator.py
# 학습 맥락 연결 및 답변 생성 로직

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ContextIntegrator:
    """학습 맥락 통합 및 답변 생성기"""
    
    def __init__(self):
        """맥락 통합기 초기화"""
        self.answer_templates = {
            'theory_explanation': self._generate_theory_answer,
            'practical_example': self._generate_practical_answer,
            'troubleshooting': self._generate_troubleshooting_answer,
            'general_question': self._generate_general_answer
        }
    
    def integrate_context_and_generate_answer(self, question: str, search_results: Dict[str, Any], 
                                            learning_context: Dict[str, Any]) -> Dict[str, Any]:
        """검색 결과와 학습 맥락을 통합하여 최종 답변 생성
        
        Args:
            question: 사용자 질문
            search_results: 검색 결과
            learning_context: 현재 학습 맥락
            
        Returns:
            Dict: 통합된 답변 결과
        """
        try:
            logger.info(f"맥락 통합 시작: {question[:50]}...")
            
            # 1. 질문 유형 분석
            question_type = self._analyze_question_type(question, learning_context)
            
            # 2. 학습 맥락 분석
            context_analysis = self._analyze_learning_context(learning_context)
            
            # 3. 검색 결과 필터링 및 우선순위 설정
            filtered_results = self._filter_and_prioritize_results(
                search_results, question_type, context_analysis
            )
            
            # 4. 답변 생성
            answer_generator = self.answer_templates.get(
                question_type, self._generate_general_answer
            )
            
            generated_answer = answer_generator(
                question, filtered_results, context_analysis
            )
            
            # 5. 최종 결과 구성
            final_result = {
                'question': question,
                'answer': generated_answer['answer'],
                'answer_type': question_type,
                'confidence_score': generated_answer.get('confidence_score', 0.7),
                'sources_used': self._extract_sources_info(filtered_results),
                'learning_context': context_analysis,
                'follow_up_suggestions': self._generate_follow_up_suggestions(
                    question, question_type, context_analysis
                ),
                'generated_at': datetime.now().isoformat()
            }
            
            logger.info(f"답변 생성 완료: 신뢰도 {final_result['confidence_score']:.2f}")
            return final_result
            
        except Exception as e:
            logger.error(f"맥락 통합 실패: {e}")
            return self._generate_error_response(question, str(e))
    
    def _analyze_question_type(self, question: str, context: Dict[str, Any]) -> str:
        """질문 유형 분석
        
        Args:
            question: 사용자 질문
            context: 학습 맥락
            
        Returns:
            str: 질문 유형
        """
        question_lower = question.lower()
        
        # 이론 설명 요청
        theory_keywords = ['무엇', '뭐', '설명', '개념', '정의', '의미', '차이']
        if any(keyword in question_lower for keyword in theory_keywords):
            return 'theory_explanation'
        
        # 실습/예시 요청
        practical_keywords = ['예시', '예제', '실습', '방법', '어떻게', '사용법', '활용']
        if any(keyword in question_lower for keyword in practical_keywords):
            return 'practical_example'
        
        # 문제 해결 요청
        troubleshooting_keywords = ['오류', '에러', '문제', '안됨', '실패', '해결']
        if any(keyword in question_lower for keyword in troubleshooting_keywords):
            return 'troubleshooting'
        
        return 'general_question'
    
    def _analyze_learning_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """학습 맥락 분석
        
        Args:
            context: 원본 학습 맥락
            
        Returns:
            Dict: 분석된 맥락 정보
        """
        return {
            'current_chapter': context.get('current_chapter', 1),
            'chapter_name': self._get_chapter_name(context.get('current_chapter', 1)),
            'user_level': context.get('user_level', 'medium'),
            'user_type': context.get('user_type', 'beginner'),
            'recent_topics': self._extract_recent_topics(context),
            'learning_progress': context.get('learning_progress', {}),
            'current_stage': context.get('current_stage', 'theory')
        }
    
    def _get_chapter_name(self, chapter_id: int) -> str:
        """챕터 ID로 챕터 이름 반환
        
        Args:
            chapter_id: 챕터 ID
            
        Returns:
            str: 챕터 이름
        """
        chapter_names = {
            1: "AI는 무엇인가?",
            2: "머신러닝의 기초",
            3: "프롬프트란 무엇인가?",
            4: "ChatGPT 활용법",
            5: "AI 윤리와 한계"
        }
        return chapter_names.get(chapter_id, f"챕터 {chapter_id}")
    
    def _extract_recent_topics(self, context: Dict[str, Any]) -> List[str]:
        """최근 학습 주제 추출
        
        Args:
            context: 학습 맥락
            
        Returns:
            List[str]: 최근 주제 목록
        """
        recent_topics = []
        
        # 최근 루프 요약에서 주제 추출
        recent_loops = context.get('recent_loops_summary', [])
        for loop in recent_loops[-3:]:  # 최근 3개 루프
            if isinstance(loop, dict) and 'topics' in loop:
                recent_topics.extend(loop['topics'])
        
        return list(set(recent_topics))  # 중복 제거
    
    def _filter_and_prioritize_results(self, search_results: Dict[str, Any], 
                                     question_type: str, context_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """검색 결과 필터링 및 우선순위 설정
        
        Args:
            search_results: 검색 결과
            question_type: 질문 유형
            context_analysis: 맥락 분석 결과
            
        Returns:
            List[Dict]: 필터링된 결과
        """
        results = search_results.get('results', [])
        if not results:
            return []
        
        # 질문 유형별 필터링
        filtered_results = []
        current_chapter = context_analysis['current_chapter']
        
        for result in results:
            # 기본 점수 (final_score 사용)
            priority_score = result.get('final_score', 0.5)
            
            # 질문 유형별 가중치 조정
            if question_type == 'theory_explanation':
                if result.get('source') == 'chromadb':
                    priority_score += 0.2  # 내부 지식 베이스 우대
                    
            elif question_type == 'practical_example':
                if 'example' in result.get('content', '').lower():
                    priority_score += 0.15
                    
            elif question_type == 'troubleshooting':
                if any(keyword in result.get('content', '').lower() 
                      for keyword in ['해결', '방법', '오류', '문제']):
                    priority_score += 0.15
            
            # 현재 챕터 관련성 보너스
            if (result.get('metadata', {}).get('chapter_id') == current_chapter):
                priority_score += 0.1
            
            result['priority_score'] = min(priority_score, 1.0)
            filtered_results.append(result)
        
        # 우선순위 점수로 정렬
        filtered_results.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
        
        # 상위 5개 결과만 사용
        return filtered_results[:5]
    
    def _generate_theory_answer(self, question: str, results: List[Dict[str, Any]], 
                              context: Dict[str, Any]) -> Dict[str, Any]:
        """이론 설명 답변 생성
        
        Args:
            question: 질문
            results: 검색 결과
            context: 맥락 정보
            
        Returns:
            Dict: 생성된 답변
        """
        if not results:
            return {
                'answer': f'"{question}"에 대한 정보를 찾을 수 없습니다. 다른 방식으로 질문해 주세요.',
                'confidence_score': 0.3
            }
        
        # 주요 정보 추출
        main_content = results[0].get('content', '')
        user_level = context.get('user_level', 'medium')
        
        # 사용자 레벨에 맞는 답변 구성
        if user_level == 'low':
            answer_prefix = "쉽게 설명드리면, "
        elif user_level == 'high':
            answer_prefix = "전문적으로 설명하면, "
        else:
            answer_prefix = ""
        
        # 답변 구성
        answer_parts = [answer_prefix + main_content]
        
        # 추가 정보가 있으면 포함
        if len(results) > 1:
            additional_info = results[1].get('content', '')
            if additional_info and len(additional_info) > 50:
                answer_parts.append(f"\n\n추가로, {additional_info}")
        
        # 현재 챕터와의 연관성 언급
        chapter_name = context.get('chapter_name', '')
        if chapter_name:
            answer_parts.append(f"\n\n이는 현재 학습 중인 '{chapter_name}' 챕터와 관련된 내용입니다.")
        
        final_answer = ''.join(answer_parts)
        
        # 신뢰도 계산 (검색 결과 품질 기반)
        confidence_score = min(
            sum(r.get('priority_score', 0.5) for r in results[:2]) / 2,
            0.9
        )
        
        return {
            'answer': final_answer,
            'confidence_score': confidence_score
        }
    
    def _generate_practical_answer(self, question: str, results: List[Dict[str, Any]], 
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """실습/예시 답변 생성
        
        Args:
            question: 질문
            results: 검색 결과
            context: 맥락 정보
            
        Returns:
            Dict: 생성된 답변
        """
        if not results:
            return {
                'answer': f'"{question}"에 대한 실습 예시를 찾을 수 없습니다. 구체적인 상황을 알려주시면 더 도움을 드릴 수 있습니다.',
                'confidence_score': 0.3
            }
        
        # 실습 관련 내용 우선 선택
        practical_results = [r for r in results if 'example' in r.get('content', '').lower() or 
                           'practice' in r.get('content', '').lower()]
        
        if not practical_results:
            practical_results = results[:2]
        
        answer_parts = ["실습 예시를 알려드리겠습니다:\n"]
        
        for i, result in enumerate(practical_results[:2], 1):
            content = result.get('content', '')
            answer_parts.append(f"\n{i}. {content}")
        
        # 사용자 유형별 추가 안내
        user_type = context.get('user_type', 'beginner')
        if user_type == 'business':
            answer_parts.append("\n\n실무에서 활용할 때는 구체적인 업무 상황에 맞게 조정해서 사용하시기 바랍니다.")
        else:
            answer_parts.append("\n\n천천히 따라해보시고, 궁금한 점이 있으면 언제든 질문해 주세요.")
        
        final_answer = ''.join(answer_parts)
        
        confidence_score = min(
            sum(r.get('priority_score', 0.5) for r in practical_results) / len(practical_results),
            0.85
        )
        
        return {
            'answer': final_answer,
            'confidence_score': confidence_score
        }
    
    def _generate_troubleshooting_answer(self, question: str, results: List[Dict[str, Any]], 
                                       context: Dict[str, Any]) -> Dict[str, Any]:
        """문제 해결 답변 생성
        
        Args:
            question: 질문
            results: 검색 결과
            context: 맥락 정보
            
        Returns:
            Dict: 생성된 답변
        """
        if not results:
            return {
                'answer': f'"{question}"에 대한 해결 방법을 찾을 수 없습니다. 문제 상황을 더 자세히 설명해 주시면 도움을 드릴 수 있습니다.',
                'confidence_score': 0.3
            }
        
        answer_parts = ["문제 해결 방법을 안내해드리겠습니다:\n"]
        
        # 해결 방법 관련 내용 우선 선택
        solution_results = [r for r in results if any(keyword in r.get('content', '').lower() 
                                                    for keyword in ['해결', '방법', '단계'])]
        
        if not solution_results:
            solution_results = results[:2]
        
        for i, result in enumerate(solution_results[:3], 1):
            content = result.get('content', '')
            answer_parts.append(f"\n{i}. {content}")
        
        answer_parts.append("\n\n위 방법으로도 해결되지 않으면, 구체적인 오류 메시지나 상황을 알려주세요.")
        
        final_answer = ''.join(answer_parts)
        
        confidence_score = min(
            sum(r.get('priority_score', 0.5) for r in solution_results) / len(solution_results),
            0.8
        )
        
        return {
            'answer': final_answer,
            'confidence_score': confidence_score
        }
    
    def _generate_general_answer(self, question: str, results: List[Dict[str, Any]], 
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """일반 질문 답변 생성
        
        Args:
            question: 질문
            results: 검색 결과
            context: 맥락 정보
            
        Returns:
            Dict: 생성된 답변
        """
        if not results:
            return {
                'answer': f'"{question}"에 대한 정보를 찾을 수 없습니다. 질문을 다시 정리해서 물어보시거나, 관련된 키워드를 포함해서 질문해 주세요.',
                'confidence_score': 0.2
            }
        
        # 가장 관련성 높은 결과 사용
        main_result = results[0]
        main_content = main_result.get('content', '')
        
        answer_parts = [main_content]
        
        # 추가 정보가 있으면 간략히 포함
        if len(results) > 1:
            additional_content = results[1].get('content', '')
            if additional_content and len(additional_content) > 30:
                answer_parts.append(f"\n\n관련 정보: {additional_content[:200]}...")
        
        final_answer = ''.join(answer_parts)
        
        confidence_score = main_result.get('priority_score', 0.6)
        
        return {
            'answer': final_answer,
            'confidence_score': confidence_score
        }
    
    def _extract_sources_info(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """검색 결과에서 출처 정보 추출
        
        Args:
            results: 검색 결과
            
        Returns:
            List[Dict]: 출처 정보
        """
        sources = []
        
        for result in results:
            source_info = {
                'source_type': result.get('source', 'unknown'),
                'priority_score': result.get('priority_score', 0),
                'title': result.get('title', ''),
                'link': result.get('link', '')
            }
            
            # ChromaDB 결과의 경우 메타데이터 포함
            if result.get('source') == 'chromadb' and 'metadata' in result:
                metadata = result['metadata']
                source_info.update({
                    'chapter_id': metadata.get('chapter_id'),
                    'content_type': metadata.get('content_type')
                })
            
            sources.append(source_info)
        
        return sources
    
    def _generate_follow_up_suggestions(self, question: str, question_type: str, 
                                      context: Dict[str, Any]) -> List[str]:
        """후속 질문 제안 생성
        
        Args:
            question: 원본 질문
            question_type: 질문 유형
            context: 맥락 정보
            
        Returns:
            List[str]: 후속 질문 제안
        """
        suggestions = []
        chapter_name = context.get('chapter_name', '')
        
        if question_type == 'theory_explanation':
            suggestions = [
                f"{chapter_name}의 실습 예시를 보여주세요",
                "이 개념을 실제로 어떻게 활용하나요?",
                "관련된 다른 개념도 알려주세요"
            ]
        elif question_type == 'practical_example':
            suggestions = [
                "이 방법의 장단점은 무엇인가요?",
                "다른 방법도 있나요?",
                "실제 적용할 때 주의사항은?"
            ]
        elif question_type == 'troubleshooting':
            suggestions = [
                "이런 문제를 예방하는 방법은?",
                "비슷한 다른 오류 해결법도 알려주세요",
                "더 자세한 설명이 필요해요"
            ]
        else:
            suggestions = [
                f"{chapter_name}에서 더 알고 싶은 내용이 있나요?",
                "실습 문제를 풀어보고 싶어요",
                "다음 단계로 넘어가고 싶어요"
            ]
        
        return suggestions[:3]  # 최대 3개 제안
    
    def _generate_error_response(self, question: str, error_message: str) -> Dict[str, Any]:
        """오류 발생 시 기본 응답 생성
        
        Args:
            question: 원본 질문
            error_message: 오류 메시지
            
        Returns:
            Dict: 오류 응답
        """
        return {
            'question': question,
            'answer': '죄송합니다. 답변 생성 중 오류가 발생했습니다. 잠시 후 다시 질문해 주세요.',
            'answer_type': 'error',
            'confidence_score': 0.0,
            'sources_used': [],
            'learning_context': {},
            'follow_up_suggestions': [
                "질문을 다시 정리해서 물어보세요",
                "다른 방식으로 질문해 보세요",
                "관련 키워드를 포함해서 질문해 주세요"
            ],
            'error': True,
            'error_message': error_message,
            'generated_at': datetime.now().isoformat()
        }

# 전역 맥락 통합기 인스턴스
context_integrator = ContextIntegrator()

def generate_contextual_answer(question: str, search_results: Dict[str, Any], 
                             current_chapter: int, user_level: str, user_type: str,
                             recent_loops: List[Dict] = None) -> Dict[str, Any]:
    """맥락을 고려한 답변 생성 (편의 함수)
    
    Args:
        question: 사용자 질문
        search_results: 검색 결과
        current_chapter: 현재 챕터
        user_level: 사용자 레벨
        user_type: 사용자 유형
        recent_loops: 최근 루프 정보
        
    Returns:
        Dict: 생성된 답변
    """
    learning_context = {
        'current_chapter': current_chapter,
        'user_level': user_level,
        'user_type': user_type,
        'recent_loops_summary': recent_loops or []
    }
    
    return context_integrator.integrate_context_and_generate_answer(
        question, search_results, learning_context
    )