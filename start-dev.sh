#!/bin/bash

set -e

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  발 환경 시작${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# .env.dev 파일 확인
if [ ! -f .env.dev ]; then
    echo -e "${RED}❌ .env.dev 파일이 없습니다.${NC}"
    exit 1
fi

# docker-compose-dev.yml 파일 확인
if [ ! -f docker-compose-dev.yml ]; then
    echo -e "${RED}❌ docker-compose-dev.yml 파일이 없습니다.${NC}"
    exit 1
fi

# Docker가 실행 중인지 확인
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker가 실행되고 있지 않습니다.${NC}"
    echo -e "${YELLOW}   Docker Desktop을 실행해주세요.${NC}"
    exit 1
fi

# .env.dev에서 PROJECT_NAME 읽기
if [ -f .env.dev ]; then
    PROJECT_NAME=$(grep "^PROJECT_NAME=" .env.dev | cut -d '=' -f2 | tr -d '"')
    PROJECT_NAME=${PROJECT_NAME:-fastapi-fullstack}
else
    PROJECT_NAME="fastapi-fullstack"
fi

# 기존 컨테이너 정리 (재시작)
if [ "$(docker ps -a -q -f name=${PROJECT_NAME})" ]; then
    echo -e "${YELLOW}🔄 기존 컨테이너를 중지하고 재시작합니다...${NC}"
    docker-compose -f docker-compose-dev.yml --env-file .env.dev down -v
    echo ""
fi

echo -e "${GREEN}🚀 개발 환경 시작 중...${NC}"
echo ""

# Docker Compose 실행
docker-compose -f docker-compose-dev.yml --env-file .env.dev up -d --build

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ 개발 환경 시작 완료${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
