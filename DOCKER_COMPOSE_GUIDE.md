# Docker Compose 사용 가이드

이 프로젝트는 개발 환경과 프로덕션 환경을 위한 독립적인 Docker Compose 파일을 제공합니다.

## 📋 목차

- [파일 설명](#파일-설명)
- [로컬 개발 환경](#로컬-개발-환경)
- [프로덕션 배포](#프로덕션-배포)
- [환경 변수 설정](#환경-변수-설정)
- [문제 해결](#문제-해결)

---

## 파일 설명

### 🔧 docker-compose.dev.yml
**로컬 개발 전용** - 모든 서비스가 포함된 완전한 개발 환경

**포함된 서비스:**
- PostgreSQL (포트 5432)
- FastAPI 백엔드 (포트 8000) - 자동 재로드
- React 프론트엔드 (포트 5173)
- Adminer - DB 관리 (포트 8080)
- MailCatcher - 이메일 테스트 (포트 1080, 1025)
- Playwright - E2E 테스트 (선택적)

**특징:**
- ✅ 모든 포트 직접 노출
- ✅ 파일 변경 시 자동 재로드
- ✅ 실시간 코드 동기화
- ✅ 개발용 기본값 제공
- ❌ HTTPS 없음
- ❌ Traefik 없음

---

### 🚀 docker-compose.prod.yml
**프로덕션 배포 전용** - Traefik을 포함한 전체 스택

**포함된 서비스:**
- Traefik (포트 80, 443) - 리버스 프록시
- PostgreSQL (내부 네트워크만)
- FastAPI 백엔드 (Traefik을 통해 접근)
- React 프론트엔드 (Traefik을 통해 접근)
- Adminer (Traefik을 통해 접근)

**특징:**
- ✅ 자동 HTTPS (Let's Encrypt)
- ✅ 도메인 기반 라우팅
- ✅ 프로덕션 최적화
- ✅ 자동 재시작
- ✅ 보안 네트워크 분리
- ❌ 파일 동기화 없음

---

## 로컬 개발 환경

### 1. 최소 환경 변수 설정

`.env.dev` 파일을 생성하거나 환경 변수를 export:

```bash
# 최소 필수 설정 (기본값 제공됨)
export POSTGRES_PASSWORD=dev_password_123
export POSTGRES_USER=postgres
export POSTGRES_DB=app
```

### 2. 개발 환경 시작

```bash
# 모든 서비스 시작 + 파일 감시
docker compose -f docker-compose.dev.yml up --watch

# 또는 백그라운드 실행
docker compose -f docker-compose.dev.yml up -d

# 로그 확인
docker compose -f docker-compose.dev.yml logs -f
```

### 3. 접속 URL

| 서비스 | URL | 설명 |
|--------|-----|------|
| 프론트엔드 | http://localhost:5173 | React 앱 |
| 백엔드 API | http://localhost:8000 | FastAPI |
| API 문서 | http://localhost:8000/docs | Swagger UI |
| Adminer | http://localhost:8080 | DB 관리 |
| MailCatcher | http://localhost:1080 | 이메일 확인 |
| PostgreSQL | localhost:5432 | 직접 연결 |

### 4. 기본 로그인 정보

- **이메일**: admin@example.com
- **비밀번호**: changethis

### 5. 개발 중 유용한 명령어

```bash
# 특정 서비스만 재시작
docker compose -f docker-compose.dev.yml restart backend

# 백엔드 컨테이너 접속
docker compose -f docker-compose.dev.yml exec backend bash

# 데이터베이스 마이그레이션
docker compose -f docker-compose.dev.yml exec backend alembic upgrade head

# 모든 컨테이너 중지 및 삭제
docker compose -f docker-compose.dev.yml down

# 볼륨까지 모두 삭제 (데이터 초기화)
docker compose -f docker-compose.dev.yml down -v
```

### 6. E2E 테스트 실행

```bash
# Playwright 테스트 실행
docker compose -f docker-compose.dev.yml --profile testing up playwright

# 테스트만 실행하고 종료
docker compose -f docker-compose.dev.yml run --rm playwright npx playwright test
```

---

## 프로덕션 배포

### 1. 필수 환경 변수 설정

프로덕션용 `.env.prod` 파일 생성:

```bash
# 도메인 설정
DOMAIN=example.com
ACME_EMAIL=admin@example.com

# Docker 이미지
DOCKER_IMAGE_BACKEND=your-registry/backend
DOCKER_IMAGE_FRONTEND=your-registry/frontend
TAG=latest

# Traefik 대시보드 인증 (htpasswd 형식)
# 생성: echo $(htpasswd -nb admin your_password)
TRAEFIK_AUTH=admin:$$apr1$$xyz...

# 데이터베이스
POSTGRES_PASSWORD=strong_prod_password
POSTGRES_USER=postgres
POSTGRES_DB=app

# 백엔드 보안
SECRET_KEY=your-super-secret-key-min-32-chars
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=strong_admin_password

# CORS (쉼표로 구분)
BACKEND_CORS_ORIGINS=https://dashboard.example.com,https://api.example.com

# 이메일 설정 (실제 SMTP 서버)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_TLS=true
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=noreply@example.com

# 선택적
SENTRY_DSN=https://your-sentry-dsn
ENVIRONMENT=production
```

### 2. 시크릿 키 생성

```bash
# SECRET_KEY 생성
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Traefik 인증 생성 (htpasswd 필요)
sudo apt-get install apache2-utils  # Ubuntu/Debian
brew install httpd  # macOS

# 사용자 생성
htpasswd -nb admin your_password
# 출력: admin:$apr1$xyz...
# .env.prod 파일에 넣을 때는 $ 를 $$ 로 이스케이프
```

### 3. DNS 설정

도메인의 DNS에 다음 레코드 추가:

```
A     example.com           → YOUR_SERVER_IP
A     api.example.com       → YOUR_SERVER_IP
A     dashboard.example.com → YOUR_SERVER_IP
A     adminer.example.com   → YOUR_SERVER_IP
A     traefik.example.com   → YOUR_SERVER_IP
```

또는 와일드카드 사용:

```
A     example.com     → YOUR_SERVER_IP
A     *.example.com   → YOUR_SERVER_IP
```

### 4. 서버 준비

```bash
# Docker 설치 (Ubuntu 예시)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker Compose V2 확인
docker compose version
```

### 5. 프로덕션 배포

```bash
# 1. 환경 변수 로드
source .env.prod
# 또는
export $(cat .env.prod | xargs)

# 2. 이미지 빌드 (선택적, 레지스트리 사용 시 생략)
docker compose -f docker-compose.prod.yml build

# 3. 스택 시작
docker compose -f docker-compose.prod.yml up -d

# 4. 로그 확인
docker compose -f docker-compose.prod.yml logs -f

# 5. 상태 확인
docker compose -f docker-compose.prod.yml ps
```

### 6. 접속 URL

| 서비스 | URL | 설명 |
|--------|-----|------|
| 프론트엔드 | https://dashboard.example.com | React 앱 |
| 백엔드 API | https://api.example.com | FastAPI |
| API 문서 | https://api.example.com/docs | Swagger UI |
| Adminer | https://adminer.example.com | DB 관리 |
| Traefik | https://traefik.example.com | 프록시 대시보드 |

### 7. 프로덕션 관리 명령어

```bash
# 서비스 재시작
docker compose -f docker-compose.prod.yml restart backend

# 로그 확인
docker compose -f docker-compose.prod.yml logs -f backend

# 이미지 업데이트 및 재배포
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d

# 데이터베이스 백업
docker compose -f docker-compose.prod.yml exec db pg_dump -U postgres app > backup.sql

# 데이터베이스 복원
docker compose -f docker-compose.prod.yml exec -T db psql -U postgres app < backup.sql

# 볼륨 확인
docker volume ls | grep prod

# 전체 중지 (데이터 유지)
docker compose -f docker-compose.prod.yml down

# 완전 삭제 (주의! 데이터 손실)
docker compose -f docker-compose.prod.yml down -v
```

---

## 환경 변수 설정

### 개발 환경 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| POSTGRES_PASSWORD | changethis | DB 비밀번호 |
| POSTGRES_USER | postgres | DB 사용자 |
| POSTGRES_DB | app | DB 이름 |
| SECRET_KEY | changethis-secret-key-for-dev | JWT 시크릿 |
| FIRST_SUPERUSER | admin@example.com | 관리자 이메일 |
| FIRST_SUPERUSER_PASSWORD | changethis | 관리자 비밀번호 |

### 프로덕션 필수 변수

| 변수 | 예시 | 설명 |
|------|------|------|
| DOMAIN | example.com | 기본 도메인 |
| ACME_EMAIL | admin@example.com | Let's Encrypt 이메일 |
| TRAEFIK_AUTH | admin:$$apr1$$... | Traefik 인증 |
| SECRET_KEY | (32자 이상) | **반드시 변경!** |
| POSTGRES_PASSWORD | (강력한 비밀번호) | **반드시 변경!** |
| FIRST_SUPERUSER_PASSWORD | (강력한 비밀번호) | **반드시 변경!** |
| DOCKER_IMAGE_BACKEND | registry/backend | 백엔드 이미지 |
| DOCKER_IMAGE_FRONTEND | registry/frontend | 프론트엔드 이미지 |

---

## 문제 해결

### 개발 환경

**문제: 포트가 이미 사용 중**
```bash
# 사용 중인 프로세스 확인
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# 포트 변경 또는 프로세스 종료
```

**문제: 파일 변경이 감지되지 않음**
```bash
# --watch 플래그 확인
docker compose -f docker-compose.dev.yml up --watch

# 수동으로 재시작
docker compose -f docker-compose.dev.yml restart backend
```

**문제: 데이터베이스 연결 실패**
```bash
# DB가 준비될 때까지 대기
docker compose -f docker-compose.dev.yml logs db

# 헬스체크 확인
docker compose -f docker-compose.dev.yml ps
```

---

### 프로덕션 환경

**문제: Let's Encrypt 인증서 발급 실패**

1. DNS가 올바르게 설정되었는지 확인:
```bash
nslookup api.example.com
```

2. 포트 80/443이 열려있는지 확인:
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

3. Traefik 로그 확인:
```bash
docker compose -f docker-compose.prod.yml logs traefik
```

**문제: 서비스가 Traefik에 등록되지 않음**

```bash
# Traefik 네트워크 확인
docker network ls | grep traefik-public

# 서비스가 올바른 네트워크에 연결되었는지 확인
docker compose -f docker-compose.prod.yml ps

# Traefik 대시보드에서 확인
# https://traefik.example.com
```

**문제: CORS 오류**

`.env.prod`의 `BACKEND_CORS_ORIGINS` 확인:
```bash
BACKEND_CORS_ORIGINS=https://dashboard.example.com,https://api.example.com
```

---

## 비교표

| 기능 | docker-compose.dev.yml | docker-compose.prod.yml |
|------|----------------------|------------------------|
| **Traefik** | ❌ 없음 | ✅ 포함 |
| **HTTPS** | ❌ | ✅ 자동 |
| **포트 노출** | ✅ 모두 | ❌ Traefik만 |
| **자동 재로드** | ✅ | ❌ |
| **파일 동기화** | ✅ | ❌ |
| **MailCatcher** | ✅ | ❌ |
| **재시작 정책** | no | always |
| **최적화** | 개발 편의성 | 프로덕션 성능 |
| **기본값** | ✅ 제공 | ❌ 필수 입력 |

---

## 추가 리소스

- [Docker Compose 문서](https://docs.docker.com/compose/)
- [Traefik 문서](https://doc.traefik.io/traefik/)
- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [Let's Encrypt](https://letsencrypt.org/)

---

## 기여

문제가 있거나 개선 사항이 있으면 이슈를 열어주세요!
