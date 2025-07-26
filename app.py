# app.py
# Flask 메인 애플리케이션

from flask import Flask
from flask_cors import CORS
from config import Config
from utils.langsmith_config import initialize_langsmith

def create_app():
    """Flask 애플리케이션 팩토리"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
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
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(learning_bp, url_prefix='/api/learning')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(feedback_bp, url_prefix='/api/feedback')
    app.register_blueprint(ui_sync_bp, url_prefix='/api/ui')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)