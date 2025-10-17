#!/bin/bash

# 프로덕션 환경 실행 스크립트
# 사용법: ./run_prod.sh [up|down|restart|logs|build]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 환경 파일 확인
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ 오류: $ENV_FILE 파일이 없습니다.${NC}"
    echo -e "${YELLOW}💡 .env.prod 파일을 생성하고 필수 값들을 설정해주세요.${NC}"
    exit 1
fi

# 필수 환경 변수 확인
source "$ENV_FILE"

MISSING_VARS=()
[ -z "$PROJECT_NAME" ] && MISSING_VARS+=("PROJECT_NAME")
[ -z "$DOMAIN" ] && MISSING_VARS+=("DOMAIN")
[ -z "$POSTGRES_PASSWORD" ] && MISSING_VARS+=("POSTGRES_PASSWORD")
[ -z "$SECRET_KEY" ] && MISSING_VARS+=("SECRET_KEY")

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo -e "${RED}❌ 오류: 다음 환경 변수가 설정되지 않았습니다:${NC}"
    for var in "${MISSING_VARS[@]}"; do
        echo -e "  - ${YELLOW}$var${NC}"
    done
    echo ""
    echo -e "${YELLOW}💡 .env.prod 파일을 확인해주세요.${NC}"
    exit 1
fi

# 명령어 처리
COMMAND=${1:-up}

case $COMMAND in
    up)
        echo -e "${BLUE}🚀 프로덕션 환경을 시작합니다...${NC}"
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
        echo -e "${GREEN}✅ 프로덕션 환경이 시작되었습니다.${NC}"
        echo ""
        echo -e "${YELLOW}접속 주소:${NC}"
        echo -e "  - 프론트엔드: ${BLUE}http://${DOMAIN}:3000${NC}"
        echo -e "  - 백엔드 API: ${BLUE}http://${DOMAIN}:8000${NC}"
        echo -e "  - API 문서: ${BLUE}http://${DOMAIN}:8000/docs${NC}"
        echo -e "  - Adminer: ${BLUE}http://${DOMAIN}:8080${NC}"
        ;;

    up-fg|foreground)
        echo -e "${BLUE}🚀 프로덕션 환경을 포그라운드로 시작합니다...${NC}"
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up
        ;;

    down)
        echo -e "${YELLOW}🛑 프로덕션 환경을 중지합니다...${NC}"
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
        echo -e "${GREEN}✅ 프로덕션 환경이 중지되었습니다.${NC}"
        ;;

    down-v|clean)
        echo -e "${RED}⚠️  경고: 이 작업은 모든 데이터를 삭제합니다!${NC}"
        read -p "정말 진행하시겠습니까? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            echo -e "${RED}🗑️  프로덕션 환경을 중지하고 볼륨을 삭제합니다...${NC}"
            docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down -v
            echo -e "${GREEN}✅ 프로덕션 환경과 데이터가 삭제되었습니다.${NC}"
        else
            echo -e "${YELLOW}❌ 작업이 취소되었습니다.${NC}"
        fi
        ;;

    restart)
        echo -e "${YELLOW}🔄 프로덕션 환경을 재시작합니다...${NC}"
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" restart
        echo -e "${GREEN}✅ 프로덕션 환경이 재시작되었습니다.${NC}"
        ;;

    logs)
        SERVICE=${2:-}
        if [ -z "$SERVICE" ]; then
            echo -e "${BLUE}📋 전체 로그를 확인합니다...${NC}"
            docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" logs -f
        else
            echo -e "${BLUE}📋 $SERVICE 로그를 확인합니다...${NC}"
            docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" logs -f "$SERVICE"
        fi
        ;;

    build)
        echo -e "${BLUE}🔨 이미지를 다시 빌드합니다...${NC}"
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build
        echo -e "${GREEN}✅ 빌드가 완료되었습니다.${NC}"
        ;;

    rebuild)
        echo -e "${BLUE}🔨 이미지를 다시 빌드하고 시작합니다...${NC}"
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up --build -d
        echo -e "${GREEN}✅ 프로덕션 환경이 재빌드되고 시작되었습니다.${NC}"
        ;;

    pull)
        echo -e "${BLUE}📥 최신 이미지를 다운로드합니다...${NC}"
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull
        echo -e "${GREEN}✅ 이미지 다운로드가 완료되었습니다.${NC}"
        ;;

    update)
        echo -e "${BLUE}🔄 최신 이미지로 업데이트합니다...${NC}"
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
        echo -e "${GREEN}✅ 업데이트가 완료되었습니다.${NC}"
        ;;

    ps|status)
        echo -e "${BLUE}📊 프로덕션 환경 상태:${NC}"
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps
        ;;

    backup-db)
        BACKUP_DIR="./backups"
        mkdir -p "$BACKUP_DIR"
        BACKUP_FILE="$BACKUP_DIR/db-backup-$(date +%Y%m%d-%H%M%S).sql"

        echo -e "${BLUE}💾 데이터베이스를 백업합니다...${NC}"
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T db \
            pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$BACKUP_FILE"

        echo -e "${GREEN}✅ 백업 완료: $BACKUP_FILE${NC}"
        ;;

    help|--help|-h)
        echo -e "${GREEN}프로덕션 환경 실행 스크립트${NC}"
        echo ""
        echo "사용법: ./run_prod.sh [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  up          - 프로덕션 환경 시작 (백그라운드, 기본값)"
        echo "  up-fg       - 프로덕션 환경 포그라운드로 시작"
        echo "  down        - 프로덕션 환경 중지"
        echo "  down-v      - 프로덕션 환경 중지 및 볼륨 삭제 (확인 필요)"
        echo "  restart     - 프로덕션 환경 재시작"
        echo "  logs [srv]  - 로그 보기 (선택적으로 서비스 지정)"
        echo "  build       - 이미지 다시 빌드"
        echo "  rebuild     - 이미지 다시 빌드하고 시작"
        echo "  pull        - 최신 이미지 다운로드"
        echo "  update      - 최신 이미지로 업데이트"
        echo "  ps          - 컨테이너 상태 확인"
        echo "  backup-db   - 데이터베이스 백업"
        echo "  help        - 도움말 표시"
        echo ""
        echo "예시:"
        echo "  ./run_prod.sh up         # 프로덕션 환경 시작"
        echo "  ./run_prod.sh logs       # 전체 로그 보기"
        echo "  ./run_prod.sh logs backend  # 백엔드 로그만 보기"
        ;;

    *)
        echo -e "${RED}❌ 알 수 없는 명령어: $COMMAND${NC}"
        echo -e "${YELLOW}💡 사용 가능한 명령어를 보려면 './run_prod.sh help'를 실행하세요.${NC}"
        exit 1
        ;;
esac
