#!/bin/bash

# 개발 환경 실행 스크립트
# 사용법: ./run_dev.sh [up|down|restart|logs|build]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

COMPOSE_FILE="docker-compose.dev.yml"
ENV_FILE=".env.dev"

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 환경 파일 확인
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ 오류: $ENV_FILE 파일이 없습니다.${NC}"
    echo -e "${YELLOW}💡 .env.dev 파일을 생성해주세요.${NC}"
    exit 1
fi

# 명령어 처리
COMMAND=${1:-up}

case $COMMAND in
    up)
        echo -e "${BLUE}🚀 개발 환경을 시작합니다...${NC}"
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up --watch
        ;;

    up-d|daemon)
        echo -e "${BLUE}🚀 개발 환경을 백그라운드로 시작합니다...${NC}"
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
        echo -e "${GREEN}✅ 개발 환경이 시작되었습니다.${NC}"
        echo ""
        echo -e "${YELLOW}접속 주소:${NC}"
        echo -e "  - 프론트엔드: ${BLUE}http://localhost:5173${NC}"
        echo -e "  - 백엔드 API: ${BLUE}http://localhost:8000${NC}"
        echo -e "  - API 문서: ${BLUE}http://localhost:8000/docs${NC}"
        echo -e "  - Adminer: ${BLUE}http://localhost:8080${NC}"
        ;;

    down)
        echo -e "${YELLOW}🛑 개발 환경을 중지합니다...${NC}"
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
        echo -e "${GREEN}✅ 개발 환경이 중지되었습니다.${NC}"
        ;;

    down-v|clean)
        echo -e "${RED}🗑️  개발 환경을 중지하고 볼륨을 삭제합니다...${NC}"
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down -v
        echo -e "${GREEN}✅ 개발 환경과 데이터가 삭제되었습니다.${NC}"
        ;;

    restart)
        echo -e "${YELLOW}🔄 개발 환경을 재시작합니다...${NC}"
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" restart
        echo -e "${GREEN}✅ 개발 환경이 재시작되었습니다.${NC}"
        ;;

    logs)
        echo -e "${BLUE}📋 개발 환경 로그를 확인합니다...${NC}"
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" logs -f
        ;;

    build)
        echo -e "${BLUE}🔨 이미지를 다시 빌드합니다...${NC}"
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build
        echo -e "${GREEN}✅ 빌드가 완료되었습니다.${NC}"
        ;;

    rebuild)
        echo -e "${BLUE}🔨 이미지를 다시 빌드하고 시작합니다...${NC}"
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up --build --watch
        ;;

    ps|status)
        echo -e "${BLUE}📊 개발 환경 상태:${NC}"
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps
        ;;

    help|--help|-h)
        echo -e "${GREEN}개발 환경 실행 스크립트${NC}"
        echo ""
        echo "사용법: ./run_dev.sh [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  up          - 개발 환경 시작 (watch 모드, 기본값)"
        echo "  up-d        - 개발 환경 백그라운드로 시작"
        echo "  down        - 개발 환경 중지"
        echo "  down-v      - 개발 환경 중지 및 볼륨 삭제"
        echo "  restart     - 개발 환경 재시작"
        echo "  logs        - 로그 보기"
        echo "  build       - 이미지 다시 빌드"
        echo "  rebuild     - 이미지 다시 빌드하고 시작"
        echo "  ps          - 컨테이너 상태 확인"
        echo "  help        - 도움말 표시"
        ;;

    *)
        echo -e "${RED}❌ 알 수 없는 명령어: $COMMAND${NC}"
        echo -e "${YELLOW}💡 사용 가능한 명령어를 보려면 './run_dev.sh help'를 실행하세요.${NC}"
        exit 1
        ;;
esac
