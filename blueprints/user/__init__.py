# blueprints/user/__init__.py
# 사용자 관련 API Blueprint 패키지

from flask import Blueprint
from .profile import profile_bp
from .stats import stats_bp

# 사용자 관련 메인 블루프린트 생성
user_bp = Blueprint('user', __name__)

# 하위 블루프린트 등록
user_bp.register_blueprint(profile_bp, url_prefix='/profile')
user_bp.register_blueprint(stats_bp, url_prefix='/stats')