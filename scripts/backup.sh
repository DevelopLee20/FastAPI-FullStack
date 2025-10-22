#!/bin/bash

# PostgreSQL 백업 스크립트
# Docker 컨테이너 환경에서 실행됩니다.

set -e

# 환경 변수 확인
if [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_DB" ]; then
    echo "Error: POSTGRES_USER and POSTGRES_DB environment variables must be set"
    exit 1
fi

# 백업 디렉토리
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/postgres_backup_${DATE}.sql.gz"

# 백업 디렉토리 생성
mkdir -p ${BACKUP_DIR}

echo "Starting PostgreSQL backup at $(date)"
echo "Backup file: ${BACKUP_FILE}"

# PostgreSQL 백업 실행
PGPASSWORD=${POSTGRES_PASSWORD} pg_dump \
    -h postgres \
    -U ${POSTGRES_USER} \
    -d ${POSTGRES_DB} \
    --clean \
    --if-exists \
    --create \
    --verbose \
    2>&1 | gzip > ${BACKUP_FILE}

if [ $? -eq 0 ]; then
    echo "Backup completed successfully at $(date)"
    echo "Backup size: $(du -h ${BACKUP_FILE} | cut -f1)"

    # 7일 이전 백업 파일 삭제
    find ${BACKUP_DIR} -name "postgres_backup_*.sql.gz" -mtime +7 -delete
    echo "Old backups (>7 days) cleaned up"
else
    echo "Backup failed!"
    exit 1
fi

# 백업 파일 개수 출력
echo "Total backup files: $(ls -1 ${BACKUP_DIR}/postgres_backup_*.sql.gz 2>/dev/null | wc -l)"
