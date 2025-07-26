# services/chromadb_service.py
# ChromaDB 벡터 데이터베이스 관리 서비스

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
import uuid

# ChromaDB 도구 임포트
from tools.external.chromadb_tool import chromadb_tool, add_learning_content

logger = logging.getLogger(__name__)

class ChromaDBService:
    """ChromaDB 벡터 데이터베이스 관리 서비스"""
    
    def __init__(self):
        """ChromaDB 서비스 초기화"""
        self.chromadb_tool = chromadb_tool
        self.default_collections = {
            'ai_learning_content': '일반 AI 학습 콘텐츠',
            'chapter_content': '챕터별 학습 콘텐츠',
            'faq_content': '자주 묻는 질문',
            'example_content': '실습 예시 콘텐츠'
        }
        
    def initialize_learning_content(self) -> bool:
        """기본 학습 콘텐츠 초기화
        
        Returns:
            bool: 초기화 성공 여부
        """
        try:
            logger.info("기본 학습 콘텐츠 초기화 시작")
            
            # 챕터 1: AI는 무엇인가? 콘텐츠
            chapter1_contents = [
                {
                    'content': 'AI(인공지능)는 인간의 지능을 모방하여 학습, 추론, 인식 등의 작업을 수행하는 컴퓨터 시스템입니다. AI는 크게 약한 AI(Narrow AI)와 강한 AI(General AI)로 구분됩니다.',
                    'chapter_id': 1,
                    'content_type': 'theory',
                    'topic': 'AI 정의',
                    'level': 'low'
                },
                {
                    'content': '머신러닝(Machine Learning)은 AI의 하위 분야로, 데이터를 통해 패턴을 학습하고 예측을 수행하는 기술입니다. 지도학습, 비지도학습, 강화학습으로 구분됩니다.',
                    'chapter_id': 1,
                    'content_type': 'theory',
                    'topic': '머신러닝',
                    'level': 'medium'
                },
                {
                    'content': '딥러닝(Deep Learning)은 머신러닝의 한 분야로, 인공신경망을 여러 층으로 쌓아 복잡한 패턴을 학습하는 기술입니다. 이미지 인식, 자연어 처리 등에서 뛰어난 성능을 보입니다.',
                    'chapter_id': 1,
                    'content_type': 'theory',
                    'topic': '딥러닝',
                    'level': 'high'
                },
                {
                    'content': 'AI 활용 예시: 1) 이미지 분류 - 사진에서 객체 인식, 2) 자연어 처리 - 번역, 요약, 3) 추천 시스템 - 개인화된 콘텐츠 추천, 4) 자율주행 - 실시간 환경 인식 및 판단',
                    'chapter_id': 1,
                    'content_type': 'example',
                    'topic': 'AI 활용 사례',
                    'level': 'medium'
                }
            ]
            
            # 챕터 3: 프롬프트란 무엇인가? 콘텐츠
            chapter3_contents = [
                {
                    'content': '프롬프트(Prompt)는 AI 언어모델에게 주는 명령이나 질문입니다. 좋은 프롬프트는 명확하고 구체적이며, 원하는 결과를 얻기 위한 충분한 맥락을 포함해야 합니다.',
                    'chapter_id': 3,
                    'content_type': 'theory',
                    'topic': '프롬프트 정의',
                    'level': 'low'
                },
                {
                    'content': '효과적인 프롬프트 작성법: 1) 명확한 지시사항 제공, 2) 예시 포함, 3) 역할 설정 (당신은 ~전문가입니다), 4) 출력 형식 지정, 5) 단계별 사고 요청',
                    'chapter_id': 3,
                    'content_type': 'theory',
                    'topic': '프롬프트 작성법',
                    'level': 'medium'
                },
                {
                    'content': '프롬프트 예시 - 요약: "다음 텍스트를 3줄로 요약해주세요. 핵심 내용만 포함하고 전문용어는 쉽게 설명해주세요: [텍스트 내용]"',
                    'chapter_id': 3,
                    'content_type': 'example',
                    'topic': '프롬프트 예시',
                    'level': 'low'
                },
                {
                    'content': '고급 프롬프트 기법: Chain-of-Thought (단계별 사고), Few-shot Learning (예시 기반 학습), Role Playing (역할 연기), Template 활용',
                    'chapter_id': 3,
                    'content_type': 'theory',
                    'topic': '고급 프롬프트 기법',
                    'level': 'high'
                }
            ]
            
            # FAQ 콘텐츠
            faq_contents = [
                {
                    'content': 'Q: AI와 머신러닝의 차이점은? A: AI는 더 넓은 개념으로 인간의 지능을 모방하는 모든 기술을 포함하며, 머신러닝은 AI를 구현하는 방법 중 하나입니다.',
                    'chapter_id': 1,
                    'content_type': 'faq',
                    'topic': 'AI vs ML',
                    'level': 'medium'
                },
                {
                    'content': 'Q: ChatGPT는 어떻게 작동하나요? A: ChatGPT는 대규모 언어모델(LLM)로, 인터넷의 방대한 텍스트 데이터를 학습하여 인간과 유사한 텍스트를 생성합니다.',
                    'chapter_id': 3,
                    'content_type': 'faq',
                    'topic': 'ChatGPT 작동원리',
                    'level': 'medium'
                },
                {
                    'content': 'Q: 프롬프트가 잘 작동하지 않을 때는? A: 1) 더 구체적으로 작성, 2) 예시 추가, 3) 단계별로 나누어 요청, 4) 다른 표현으로 재작성해보세요.',
                    'chapter_id': 3,
                    'content_type': 'faq',
                    'topic': '프롬프트 문제해결',
                    'level': 'low'
                }
            ]
            
            # 모든 콘텐츠 추가
            all_contents = chapter1_contents + chapter3_contents + faq_contents
            
            success_count = 0
            for content_data in all_contents:
                success = add_learning_content(
                    content=content_data['content'],
                    chapter_id=content_data['chapter_id'],
                    content_type=content_data['content_type'],
                    topic=content_data['topic']
                )
                if success:
                    success_count += 1
                    
            logger.info(f"학습 콘텐츠 초기화 완료: {success_count}/{len(all_contents)}개 성공")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"학습 콘텐츠 초기화 실패: {e}")
            return False
    
    def add_chapter_content(self, chapter_id: int, content_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """챕터별 콘텐츠 일괄 추가
        
        Args:
            chapter_id: 챕터 ID
            content_list: 추가할 콘텐츠 리스트
            
        Returns:
            Dict: 추가 결과
        """
        try:
            results = {
                'chapter_id': chapter_id,
                'total_contents': len(content_list),
                'success_count': 0,
                'failed_contents': [],
                'added_contents': []
            }
            
            for content_data in content_list:
                success = add_learning_content(
                    content=content_data.get('content', ''),
                    chapter_id=chapter_id,
                    content_type=content_data.get('content_type', 'theory'),
                    topic=content_data.get('topic', 'general')
                )
                
                if success:
                    results['success_count'] += 1
                    results['added_contents'].append({
                        'topic': content_data.get('topic'),
                        'content_type': content_data.get('content_type'),
                        'length': len(content_data.get('content', ''))
                    })
                else:
                    results['failed_contents'].append(content_data.get('topic', 'unknown'))
            
            logger.info(f"챕터 {chapter_id} 콘텐츠 추가: {results['success_count']}/{results['total_contents']}개 성공")
            return results
            
        except Exception as e:
            logger.error(f"챕터 콘텐츠 추가 실패: {e}")
            return {
                'chapter_id': chapter_id,
                'error': str(e),
                'success_count': 0
            }
    
    def search_similar_content(self, query: str, chapter_id: Optional[int] = None, 
                             content_type: Optional[str] = None, 
                             max_results: int = 5) -> List[Dict[str, Any]]:
        """유사 콘텐츠 검색 (고급 필터링)
        
        Args:
            query: 검색 쿼리
            chapter_id: 특정 챕터로 제한
            content_type: 콘텐츠 유형 필터 (theory, example, faq)
            max_results: 최대 결과 수
            
        Returns:
            List[Dict]: 검색 결과
        """
        try:
            # 기본 검색 실행
            results = self.chromadb_tool.search_similar_content(
                query=query,
                n_results=max_results * 2,  # 필터링을 위해 더 많이 가져옴
                chapter_filter=chapter_id
            )
            
            # 콘텐츠 유형 필터링
            if content_type and results:
                filtered_results = []
                for result in results:
                    metadata = result.get('metadata', {})
                    if isinstance(metadata, dict) and metadata.get('content_type') == content_type:
                        filtered_results.append(result)
                results = filtered_results
            
            # 결과 수 제한
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"유사 콘텐츠 검색 실패: {e}")
            return []
    
    def get_content_statistics(self) -> Dict[str, Any]:
        """콘텐츠 통계 정보 반환
        
        Returns:
            Dict: 통계 정보
        """
        try:
            base_stats = self.chromadb_tool.get_collection_stats()
            
            # 추가 통계 정보
            enhanced_stats = {
                'basic_stats': base_stats,
                'content_distribution': {
                    'total_documents': base_stats.get('total_documents', 0)
                },
                'supported_chapters': [1, 3],  # 현재 지원하는 챕터
                'content_types': ['theory', 'example', 'faq'],
                'search_capabilities': [
                    '유사도 기반 검색',
                    '챕터별 필터링',
                    '콘텐츠 유형별 필터링',
                    '다중 조건 검색'
                ]
            }
            
            return enhanced_stats
            
        except Exception as e:
            logger.error(f"통계 조회 실패: {e}")
            return {'error': str(e)}
    
    def backup_content(self, backup_path: str = None) -> Dict[str, Any]:
        """콘텐츠 백업
        
        Args:
            backup_path: 백업 파일 경로
            
        Returns:
            Dict: 백업 결과
        """
        try:
            if not backup_path:
                backup_path = f"chromadb_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # 현재는 기본 통계만 백업 (실제 구현에서는 전체 데이터 백업)
            backup_data = {
                'backup_timestamp': datetime.now().isoformat(),
                'statistics': self.get_content_statistics(),
                'backup_path': backup_path
            }
            
            # 백업 파일 저장 (실제 구현)
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"콘텐츠 백업 완료: {backup_path}")
            return {
                'success': True,
                'backup_path': backup_path,
                'backup_size': os.path.getsize(backup_path) if os.path.exists(backup_path) else 0
            }
            
        except Exception as e:
            logger.error(f"콘텐츠 백업 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def health_check(self) -> Dict[str, Any]:
        """ChromaDB 연결 상태 확인
        
        Returns:
            Dict: 상태 정보
        """
        try:
            stats = self.chromadb_tool.get_collection_stats()
            
            health_status = {
                'status': 'healthy' if 'error' not in stats else 'unhealthy',
                'connection': 'connected' if self.chromadb_tool.client else 'disconnected',
                'collection_status': 'active' if self.chromadb_tool.collection else 'inactive',
                'total_documents': stats.get('total_documents', 0),
                'last_check': datetime.now().isoformat()
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"상태 확인 실패: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }

# 전역 ChromaDB 서비스 인스턴스
chromadb_service = ChromaDBService()

def initialize_default_content() -> bool:
    """기본 학습 콘텐츠 초기화 (편의 함수)
    
    Returns:
        bool: 초기화 성공 여부
    """
    return chromadb_service.initialize_learning_content()

def search_learning_content(query: str, chapter_id: Optional[int] = None, 
                          content_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """학습 콘텐츠 검색 (편의 함수)
    
    Args:
        query: 검색 쿼리
        chapter_id: 챕터 필터
        content_type: 콘텐츠 유형 필터
        
    Returns:
        List[Dict]: 검색 결과
    """
    return chromadb_service.search_similar_content(query, chapter_id, content_type)

def get_chromadb_health() -> Dict[str, Any]:
    """ChromaDB 상태 확인 (편의 함수)
    
    Returns:
        Dict: 상태 정보
    """
    return chromadb_service.health_check()