# tools/external/chromadb_tool.py
# ChromaDB 벡터 검색 도구

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import logging
from langchain_openai.embeddings import OpenAIEmbeddings
import os
from datetime import datetime
from .error_handler import handle_service_error, ServiceType, ErrorSeverity

logger = logging.getLogger(__name__)

class ChromaDBTool:
    """ChromaDB 벡터 검색 도구"""
    
    def __init__(self):
        """ChromaDB 클라이언트 초기화"""
        try:
            # ChromaDB 클라이언트 설정
            self.client = chromadb.PersistentClient(
                path="./chromadb_data",
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # 임베딩 모델 초기화
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=os.getenv('OPENAI_API_KEY')
            )
            
            # 컬렉션 이름 설정
            self.collection_name = "ai_learning_content"
            
            # 컬렉션 가져오기 또는 생성
            try:
                self.collection = self.client.get_collection(self.collection_name)
                logger.info(f"기존 컬렉션 '{self.collection_name}' 로드됨")
            except Exception:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "AI 학습 콘텐츠 벡터 저장소"}
                )
                logger.info(f"새 컬렉션 '{self.collection_name}' 생성됨")
                
        except Exception as e:
            logger.error(f"ChromaDB 초기화 실패: {e}")
            self.client = None
            self.collection = None
            
            # 오류 처리 시스템에 기록
            handle_service_error(
                service_type=ServiceType.CHROMADB,
                error_code="initialization_failed",
                error_message=str(e),
                context={"operation": "client_initialization"},
                severity=ErrorSeverity.CRITICAL
            )
    
    def add_content(self, content: str, metadata: Dict[str, Any], doc_id: str) -> bool:
        """학습 콘텐츠를 벡터 데이터베이스에 추가
        
        Args:
            content: 추가할 텍스트 콘텐츠
            metadata: 메타데이터 (챕터, 유형 등)
            doc_id: 문서 고유 ID
            
        Returns:
            bool: 성공 여부
        """
        try:
            if not self.collection:
                logger.error("ChromaDB 컬렉션이 초기화되지 않음")
                
                # 오류 처리 시스템에 기록
                handle_service_error(
                    service_type=ServiceType.CHROMADB,
                    error_code="collection_not_initialized",
                    error_message="ChromaDB 컬렉션이 초기화되지 않음",
                    context={"operation": "add_content", "doc_id": doc_id},
                    severity=ErrorSeverity.HIGH
                )
                return False
            
            # 텍스트 임베딩 생성
            embedding = self.embeddings.embed_query(content)
            
            # 컬렉션에 추가
            self.collection.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
            logger.info(f"콘텐츠 추가 성공: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"콘텐츠 추가 실패: {e}")
            
            # 오류 처리 시스템에 기록
            handle_service_error(
                service_type=ServiceType.CHROMADB,
                error_code="content_add_failed",
                error_message=str(e),
                context={"operation": "add_content", "doc_id": doc_id, "content_length": len(content)},
                severity=ErrorSeverity.MEDIUM
            )
            return False
    
    def search_similar_content(self, query: str, n_results: int = 5, 
                             chapter_filter: Optional[int] = None) -> List[Dict[str, Any]]:
        """유사한 콘텐츠 검색
        
        Args:
            query: 검색 쿼리
            n_results: 반환할 결과 수
            chapter_filter: 특정 챕터로 필터링 (선택사항)
            
        Returns:
            List[Dict]: 검색 결과 리스트
        """
        try:
            if not self.collection:
                logger.error("ChromaDB 컬렉션이 초기화되지 않음")
                
                # 오류 처리 시스템에 기록 및 대체 응답 반환
                fallback_result = handle_service_error(
                    service_type=ServiceType.CHROMADB,
                    error_code="collection_not_initialized",
                    error_message="ChromaDB 컬렉션이 초기화되지 않음",
                    context={"operation": "search", "query": query},
                    severity=ErrorSeverity.HIGH
                )
                
                # 대체 응답이 있으면 반환
                if fallback_result.get("is_fallback") and fallback_result.get("results"):
                    return fallback_result["results"]
                
                return []
            
            # 쿼리 임베딩 생성
            query_embedding = self.embeddings.embed_query(query)
            
            # 검색 조건 설정
            where_condition = {}
            if chapter_filter:
                where_condition["chapter_id"] = chapter_filter
            
            # 유사도 검색 실행
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_condition if where_condition else None,
                include=["documents", "metadatas", "distances"]
            )
            
            # 결과 포맷팅
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'similarity_score': 1 - results['distances'][0][i],  # 거리를 유사도로 변환
                        'source': 'chromadb'
                    })
            
            logger.info(f"검색 완료: {len(formatted_results)}개 결과 반환")
            return formatted_results
            
        except Exception as e:
            logger.error(f"검색 실패: {e}")
            
            # 오류 처리 시스템에 기록 및 대체 응답 반환
            fallback_result = handle_service_error(
                service_type=ServiceType.CHROMADB,
                error_code="search_failed",
                error_message=str(e),
                context={"operation": "search", "query": query, "n_results": n_results},
                severity=ErrorSeverity.MEDIUM
            )
            
            # 대체 응답이 있으면 반환
            if fallback_result.get("is_fallback") and fallback_result.get("results"):
                return fallback_result["results"]
            
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """컬렉션 통계 정보 반환
        
        Returns:
            Dict: 컬렉션 통계
        """
        try:
            if not self.collection:
                return {"error": "컬렉션이 초기화되지 않음"}
            
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection_name,
                "status": "active"
            }
            
        except Exception as e:
            logger.error(f"통계 조회 실패: {e}")
            return {"error": str(e)}

# 전역 ChromaDB 도구 인스턴스
chromadb_tool = ChromaDBTool()

def search_knowledge_base(query: str, chapter_id: Optional[int] = None, 
                         max_results: int = 5) -> List[Dict[str, Any]]:
    """지식 베이스에서 관련 정보 검색
    
    Args:
        query: 검색할 질문
        chapter_id: 특정 챕터로 제한 (선택사항)
        max_results: 최대 결과 수
        
    Returns:
        List[Dict]: 검색 결과
    """
    return chromadb_tool.search_similar_content(
        query=query,
        n_results=max_results,
        chapter_filter=chapter_id
    )

def add_learning_content(content: str, chapter_id: int, content_type: str, 
                        topic: str) -> bool:
    """학습 콘텐츠를 지식 베이스에 추가
    
    Args:
        content: 콘텐츠 텍스트
        chapter_id: 챕터 ID
        content_type: 콘텐츠 유형 (theory, example, faq 등)
        topic: 주제
        
    Returns:
        bool: 성공 여부
    """
    import uuid
    
    metadata = {
        "chapter_id": chapter_id,
        "content_type": content_type,
        "topic": topic,
        "created_at": str(datetime.now())
    }
    
    doc_id = f"{content_type}_{chapter_id}_{uuid.uuid4().hex[:8]}"
    
    return chromadb_tool.add_content(content, metadata, doc_id)