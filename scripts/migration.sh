#!/bin/bash
# 오류 발생 시 즉시 스크립트를 종료합니다.
set -e

# --- 설정 ---
BACKEND_DIR="../backend"

# --- 메인 스크립트 ---

# 1. 마이그레이션 메시지가 있는지 확인합니다.
if [ -z "$1" ]; then
  echo "오류: 마이그레이션 메시지가 필요합니다."
  echo "사용법: ./migration.sh \"<커밋 메시지처럼 변경 사항을 요약>\""
  exit 1
fi

# backend 디렉터리로 이동합니다.
pushd "$(dirname "$0")/$BACKEND_DIR" > /dev/null

# 2. 마이그레이션 스크립트를 생성합니다.
echo ">>> 1/3: 마이그레이션 스크립트를 생성합니다..."
pipenv run alembic revision --autogenerate -m "$1"

# 3. 생성된 스크립트를 검토하도록 안내합니다.
echo "\n>>> 2/3: 생성된 스크립트를 'backend/alembic/versions/' 폴더에서 확인하세요."
read -p "   계속하려면 Enter를, 취소하려면 Ctrl+C를 누르세요..."

# 4. 데이터베이스에 마이그레이션을 적용합니다.
echo "\n>>> 3/3: 데이터베이스에 마이그레이션을 적용합니다..."
pipenv run alembic upgrade head

# 원래 디렉터리로 돌아옵니다.
popd > /dev/null

# 5. 최종 안내사항을 출력합니다.
echo "\n✅ 마이그레이션이 성공적으로 적용되었습니다."
git status
