# 빠른 시작 가이드

## 개발 환경 (5분 안에 시작)

### 1단계: 환경 변수 확인

`.env.dev` 파일이 이미 준비되어 있습니다! 기본값으로 바로 사용 가능합니다.

```bash
# 파일 내용 확인 (선택사항)
cat .env.dev
```

### 2단계: 개발 환경 시작

```bash
docker compose -f docker-compose.dev.yml --env-file .env.dev up --watch
```

### 3단계: 접속

- 프론트엔드: http://localhost:5173
- 백엔드 API: http://localhost:8000
- API 문서: http://localhost:8000/docs
- DB 관리 (Adminer): http://localhost:8080
- 이메일 확인 (MailCatcher): http://localhost:1080

### 4단계: 로그인

- 이메일: `admin@example.com`
- 비밀번호: `changethis`

**완료! 🎉**

---

## 프로덕션 배포

### 1단계: .env.prod 파일 수정

```bash
nano .env.prod
```

**필수 변경 항목:**

1. **도메인 설정**
```
DOMAIN=your-domain.com
ACME_EMAIL=your-email@example.com
```

2. **시크릿 키 생성**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
생성된 값을 `SECRET_KEY`에 입력

3. **Traefik 인증 생성**
```bash
htpasswd -nb admin your_password
```
출력된 값에서 `$`를 `$$`로 변경하여 `TRAEFIK_AUTH`에 입력

4. **비밀번호 변경**
```
POSTGRES_PASSWORD=강력한비밀번호
FIRST_SUPERUSER_PASSWORD=관리자비밀번호
```

5. **이메일 설정** (Gmail 예시)
```
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
```

### 2단계: DNS 설정

도메인의 DNS에 A 레코드 추가:

```
A    your-domain.com           → YOUR_SERVER_IP
A    *.your-domain.com         → YOUR_SERVER_IP
```

또는 각각:
```
A    api.your-domain.com       → YOUR_SERVER_IP
A    dashboard.your-domain.com → YOUR_SERVER_IP
A    adminer.your-domain.com   → YOUR_SERVER_IP
A    traefik.your-domain.com   → YOUR_SERVER_IP
```

### 3단계: 방화벽 설정

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### 4단계: 배포

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

### 5단계: 접속

- 프론트엔드: https://dashboard.your-domain.com
- 백엔드 API: https://api.your-domain.com
- API 문서: https://api.your-domain.com/docs
- Adminer: https://adminer.your-domain.com
- Traefik: https://traefik.your-domain.com

**완료! 🚀**

---

## 자주 사용하는 명령어

### 개발 환경

```bash
# 시작
docker compose -f docker-compose.dev.yml --env-file .env.dev up --watch

# 중지
docker compose -f docker-compose.dev.yml down

# 재시작
docker compose -f docker-compose.dev.yml --env-file .env.dev restart

# 로그 보기
docker compose -f docker-compose.dev.yml logs -f

# 백엔드 컨테이너 접속
docker compose -f docker-compose.dev.yml exec backend bash
```

### 프로덕션 환경

```bash
# 시작
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d

# 중지
docker compose -f docker-compose.prod.yml down

# 재시작
docker compose -f docker-compose.prod.yml --env-file .env.prod restart

# 로그 보기
docker compose -f docker-compose.prod.yml logs -f

# 업데이트 및 재배포
docker compose -f docker-compose.prod.yml --env-file .env.prod pull
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

---

## 문제 해결

### 개발 환경: 포트가 이미 사용 중

```bash
# 사용 중인 프로세스 확인
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# 포트를 사용하는 프로세스 종료 또는 .env.dev에서 포트 변경
```

### 프로덕션: HTTPS 인증서 발급 실패

1. DNS가 올바른지 확인
```bash
nslookup api.your-domain.com
```

2. 포트가 열려있는지 확인
```bash
sudo ufw status
```

3. Traefik 로그 확인
```bash
docker compose -f docker-compose.prod.yml logs traefik
```

---

## 더 자세한 정보

전체 가이드는 [DOCKER_COMPOSE_GUIDE.md](DOCKER_COMPOSE_GUIDE.md)를 참조하세요.
