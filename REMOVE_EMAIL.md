# 이메일 기능 제거 가이드

이메일/SMTP 기능이 필요 없다면 다음과 같이 제거할 수 있습니다.

## 1. docker-compose.dev.yml 수정

### mailcatcher 서비스 제거
```yaml
# 이 부분 삭제
mailcatcher:
  image: schickling/mailcatcher
  restart: "no"
  ports:
    - "1080:1080"
    - "1025:1025"
```

### SMTP 환경 변수 제거
```yaml
backend:
  environment:
    # 이 부분 삭제
    - SMTP_HOST=mailcatcher
    - SMTP_PORT=1025
    - SMTP_TLS=false
    - SMTP_USER=
    - SMTP_PASSWORD=
```

## 2. .env.dev 수정

```bash
# 이 줄 삭제 또는 주석 처리
# EMAILS_FROM_EMAIL=noreply@example.com
```

## 3. .env.prod 수정

```bash
# SMTP 관련 줄 삭제 또는 주석 처리
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_TLS=true
# SMTP_USER=your-email@gmail.com
# SMTP_PASSWORD=your-app-password
# EMAILS_FROM_EMAIL=noreply@example.com
```

## 4. 백엔드 API 제거 (선택사항)

이메일 관련 API 엔드포인트를 제거하려면:

### backend/app/api/routes/login.py

```python
# 이 엔드포인트들 주석 처리 또는 삭제:
# - /password-recovery/{email}
# - /reset-password/
# - /password-recovery-html-content/{email}
```

또는 에러 반환하도록 수정:
```python
@router.post("/password-recovery/{email}")
def recover_password(email: str, session: SessionDep) -> Message:
    raise HTTPException(
        status_code=501,
        detail="Email functionality is disabled"
    )
```

## 5. 프론트엔드 수정 (선택사항)

### frontend/src/routes/login.tsx

"비밀번호를 잊으셨나요?" 링크 제거

## 주의사항

⚠️ **이메일 기능을 제거하면:**
- 사용자가 비밀번호를 잊어버렸을 때 복구할 방법이 없음
- 관리자가 직접 데이터베이스에서 비밀번호를 재설정해야 함

💡 **권장 사항:**
- 개발 중에는 MailCatcher를 그대로 두는 것을 권장
- 나중에 필요할 수 있으므로 코드는 유지하고 환경 변수만 설정 안 하기
