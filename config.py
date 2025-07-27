# config.py
# 설정 관리 모듈

import os
from dotenv import load_dotenv
import pymysql

# PyMySQL을 MySQLdb로 사용하도록 설정
pymysql.install_as_MySQLdb()

# .env 파일 로드
load_dotenv()

class Config:
    """애플리케이션 설정 클래스"""
    
    # Flask 기본 설정
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # 데이터베이스 설정
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'mysql://user:password@localhost/ai_literacy_navigator'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT 설정
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1시간
    
    # OpenAI API 설정
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')
    
    # ChromaDB 설정
    CHROMADB_HOST = os.environ.get('CHROMADB_HOST', 'localhost')
    CHROMADB_PORT = int(os.environ.get('CHROMADB_PORT', 8000))
    
    # 학습 설정
    MAX_LOOP_SUMMARY_COUNT = int(os.environ.get('MAX_LOOP_SUMMARY_COUNT', 5))
    DEFAULT_USER_LEVEL = os.environ.get('DEFAULT_USER_LEVEL', 'medium')
    
    # 로깅 설정
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'app.log')

class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """프로덕션 환경 설정"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """테스트 환경 설정"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# 환경별 설정 매핑
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}