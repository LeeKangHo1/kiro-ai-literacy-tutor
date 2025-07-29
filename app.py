# app.py
# Flask 메인 애플리케이션

from flask import Flask
from flask_cors import CORS
from config import Config
from utils.langsmith_config import initialize_langsmith
from utils.logging_config import LoggingConfig
from utils.error_handler import GlobalErrorHandler
from utils.performance_middleware import PerformanceMiddleware
from services.performance_service import performance_service

def create_app():
    """Flask 애플리케이션 팩토리"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # SQLAlchemy 초기화
    from models import db
    db.init_app(app)
    
    # 로깅 시스템 초기화
    LoggingConfig.setup_logging(
        app=app,
        log_level=app.config.get('LOG_LEVEL', 'INFO'),
        log_file=app.config.get('LOG_FILE', 'logs/app.log')
    )
    
    # 전역 오류 처리기 초기화
    error_handler = GlobalErrorHandler(app)
    
    # 성능 모니터링 미들웨어 초기화
    performance_middleware = PerformanceMiddleware(app)
    
    # 성능 최적화 초기화
    with app.app_context():
        performance_service.initialize_performance_optimizations()
    
    # CORS 설정
    CORS(app)
    
    # LangSmith 초기화
    initialize_langsmith()
    
    # Blueprint 등록
    from blueprints.auth import auth_bp
    from blueprints.learning import learning_bp
    from blueprints.user import user_bp
    from blueprints.feedback import feedback_bp
    from blueprints.ui_sync import ui_sync_bp
    from blueprints.monitoring import monitoring_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(learning_bp, url_prefix='/api/learning')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(feedback_bp, url_prefix='/api/feedback')
    app.register_blueprint(ui_sync_bp, url_prefix='/api/ui')
    app.register_blueprint(monitoring_bp, url_prefix='/api/monitoring')
    
    # 애플리케이션 시작 로그
    app.logger.info("AI Literacy Navigator 애플리케이션 시작")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)