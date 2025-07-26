# blueprints/learning/__init__.py
# 학습 관련 API Blueprint 패키지

from flask import Blueprint
from .progress import progress_bp

# 학습 관련 메인 블루프린트 생성
learning_bp = Blueprint('learning', __name__)

# 하위 블루프린트 등록
learning_bp.register_blueprint(progress_bp, url_prefix='/progress')