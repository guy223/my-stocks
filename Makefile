.PHONY: help test report collect query clean install

# 기본 타겟: 도움말 표시
help:
	@echo "========================================="
	@echo "  my-stocks 프로젝트 Makefile"
	@echo "========================================="
	@echo ""
	@echo "사용 가능한 명령어:"
	@echo "  make test       - 단위 테스트 실행 (pytest)"
	@echo "  make test-cov   - 테스트 + 커버리지 리포트"
	@echo "  make report     - 일일 리포트 생성"
	@echo "  make collect    - 관심 종목 데이터 수집"
	@echo "  make query      - 데이터베이스 조회"
	@echo "  make install    - 의존성 설치 (uv sync)"
	@echo "  make clean      - 캐시 및 임시 파일 삭제"
	@echo ""
	@echo "예제:"
	@echo "  make report     # 오늘 리포트 생성"
	@echo "  make test       # 모든 테스트 실행"
	@echo "  make clean      # 정리"
	@echo ""

# 단위 테스트 실행
test:
	@echo "🧪 단위 테스트 실행 중..."
	uv run pytest

# 테스트 + 커버리지 리포트
test-cov:
	@echo "🧪 테스트 및 커버리지 분석 중..."
	uv run pytest --cov=src --cov-report=html
	@echo "✅ 커버리지 리포트 생성 완료: htmlcov/index.html"

# 일일 리포트 생성
report:
	@echo "📊 일일 리포트 생성 중..."
	uv run report

# 관심 종목 데이터 수집
collect:
	@echo "📈 데이터 수집 중..."
	uv run collect

# 데이터베이스 조회
query:
	@echo "🔍 데이터베이스 조회 중..."
	uv run query

# 의존성 설치
install:
	@echo "📦 의존성 설치 중..."
	uv sync
	@echo "✅ 설치 완료"

# 캐시 및 임시 파일 삭제
clean:
	@echo "🧹 정리 중..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf build
	rm -rf dist
	@echo "✅ 정리 완료"
