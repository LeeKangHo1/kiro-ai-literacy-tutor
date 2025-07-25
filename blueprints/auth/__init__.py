# blueprints/auth/__init__.py
# 인증 관련 API Blueprint 패키지

from flask import Blueprint

# 인증 블루프린트 생성
auth_bp = Blueprint('auth', __name__)

# 각 모듈에서 라우트 임포트
from . import register, login, token