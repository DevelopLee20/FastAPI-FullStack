# FastAPI 풀스택 프로젝트

FastAPI와 React(Vite)를 기반으로 하는 풀스택 프로젝트 템플릿입니다. 애플리케이션 실행 시 PostgreSQL에 저장된 환경변수 중 일부를 Redis에 캐싱하여 빠른 조회를 지원합니다.

## 주요 명령어

프로젝트 루트 디렉터리에서 아래 스크립트들을 실행하세요.

### 개발 환경 실행

개발 서버를 시작합니다. 프론트엔드와 백엔드 모두 변경사항이 감지되면 자동으로 재시작됩니다.

```bash
./start-dev.sh
```

### 프로덕션 환경 실행

프로덕션 모드로 서버를 시작합니다.

```bash
./start-prod.sh
```

### 데이터베이스 마이그레이션

데이터베이스 스키마 변경사항을 적용합니다. `backend/app/models/` 내부의 모델 파일을 수정한 후, 아래 명령어를 실행하여 데이터베이스에 변경사항을 반영할 수 있습니다.

```bash
./scripts/migration.sh "변경사항에 대한 요약 메시지"
```

### 데이터베이스 백업

실행 중인 `backend` 컨테이너에 접속하여 PostgreSQL 데이터베이스를 백업합니다. 백업 파일은 `backend/data/backups` 디렉터리에 저장됩니다.

```bash
docker-compose exec backend ./scripts/backup.sh
```

### Docker 환경 초기화

> **⚠️ 주의: 이 스크립트는 모든 Docker 컨테이너, 이미지, 볼륨, 네트워크를 삭제하여 로컬 Docker 환경을 초기화합니다. 데이터베이스를 포함한 모든 데이터가 영구적으로 삭제되니 신중하게 사용하세요.**

```bash
./reset_docker.sh
```