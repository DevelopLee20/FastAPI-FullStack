# FastAPI 프로젝트 - 개발

## Docker Compose

* Docker Compose로 로컬 스택을 시작합니다:

```bash
docker compose watch
```

* 이제 브라우저를 열고 다음 URL과 상호 작용할 수 있습니다:

경로에 따라 라우트가 처리되는 Docker로 빌드된 프론트엔드: http://localhost:5173

OpenAPI 기반 JSON 웹 API인 백엔드: http://localhost:8000

OpenAPI 백엔드의 자동 인터랙티브 문서 (Swagger UI): http://localhost:8000/docs

데이터베이스 웹 관리 도구인 Adminer: http://localhost:8080

프록시가 라우트를 처리하는 방법을 확인하는 Traefik UI: http://localhost:8090

**참고**: 스택을 처음 시작할 때는 준비되는 데 1분 정도 걸릴 수 있습니다. 백엔드가 데이터베이스가 준비될 때까지 기다리고 모든 것을 구성하는 동안입니다. 로그를 확인하여 모니터링할 수 있습니다.

로그를 확인하려면 (다른 터미널에서) 다음을 실행합니다:

```bash
docker compose logs
```

특정 서비스의 로그를 확인하려면 서비스 이름을 추가합니다. 예:

```bash
docker compose logs backend
```

## 로컬 개발

Docker Compose 파일은 각 서비스가 `localhost`의 다른 포트에서 사용 가능하도록 구성되어 있습니다.

백엔드와 프론트엔드의 경우 로컬 개발 서버에서 사용하는 것과 동일한 포트를 사용하므로 백엔드는 `http://localhost:8000`에 있고 프론트엔드는 `http://localhost:5173`에 있습니다.

이렇게 하면 Docker Compose 서비스를 끄고 로컬 개발 서비스를 시작할 수 있으며, 모두 동일한 포트를 사용하므로 모든 것이 계속 작동합니다.

예를 들어, Docker Compose에서 `frontend` 서비스를 중지할 수 있습니다. 다른 터미널에서 다음을 실행합니다:

```bash
docker compose stop frontend
```

그런 다음 로컬 프론트엔드 개발 서버를 시작합니다:

```bash
cd frontend
npm run dev
```

또는 `backend` Docker Compose 서비스를 중지할 수 있습니다:

```bash
docker compose stop backend
```

그런 다음 백엔드용 로컬 개발 서버를 실행할 수 있습니다:

```bash
cd backend
fastapi dev app/main.py
```

## `localhost.tiangolo.com`의 Docker Compose

Docker Compose 스택을 시작하면 기본적으로 `localhost`를 사용하며 각 서비스마다 다른 포트를 사용합니다(백엔드, 프론트엔드, adminer 등).

프로덕션(또는 스테이징)에 배포하면 각 서비스가 다른 하위 도메인에 배포됩니다. 백엔드의 경우 `api.example.com`, 프론트엔드의 경우 `dashboard.example.com`과 같습니다.

[배포](deployment.md) 가이드에서 구성된 프록시인 Traefik에 대해 읽을 수 있습니다. 그것이 하위 도메인을 기반으로 각 서비스에 트래픽을 전송하는 역할을 하는 구성 요소입니다.

로컬에서 모든 것이 작동하는지 테스트하려면 로컬 `.env` 파일을 편집하고 다음을 변경할 수 있습니다:

```dotenv
DOMAIN=localhost.tiangolo.com
```

이것은 Docker Compose 파일에서 서비스의 기본 도메인을 구성하는 데 사용됩니다.

Traefik은 이것을 사용하여 `api.localhost.tiangolo.com`의 트래픽을 백엔드로, `dashboard.localhost.tiangolo.com`의 트래픽을 프론트엔드로 전송합니다.

`localhost.tiangolo.com` 도메인은 `127.0.0.1`을 가리키도록 구성된(모든 하위 도메인 포함) 특수 도메인입니다. 이렇게 하면 로컬 개발에 사용할 수 있습니다.

업데이트한 후 다시 실행합니다:

```bash
docker compose watch
```

배포할 때, 예를 들어 프로덕션에서는 메인 Traefik이 Docker Compose 파일 외부에 구성됩니다. 로컬 개발의 경우 `docker-compose.override.yml`에 Traefik이 포함되어 있어 도메인이 예상대로 작동하는지 테스트할 수 있습니다. 예를 들어 `api.localhost.tiangolo.com` 및 `dashboard.localhost.tiangolo.com`과 같습니다.

## Docker Compose 파일 및 환경 변수

전체 스택에 적용되는 모든 구성이 포함된 메인 `docker-compose.yml` 파일이 있으며, `docker compose`에서 자동으로 사용됩니다.

그리고 개발을 위한 오버라이드가 있는 `docker-compose.override.yml`도 있습니다. 예를 들어 소스 코드를 볼륨으로 마운트합니다. `docker compose`에서 자동으로 사용되어 `docker-compose.yml` 위에 오버라이드를 적용합니다.

이러한 Docker Compose 파일은 컨테이너에 환경 변수로 주입될 구성이 포함된 `.env` 파일을 사용합니다.

또한 `docker compose` 명령을 호출하기 전에 스크립트에 설정된 환경 변수에서 가져온 일부 추가 구성도 사용합니다.

변수를 변경한 후에는 스택을 다시 시작해야 합니다:

```bash
docker compose watch
```

## .env 파일

`.env` 파일은 생성된 키와 비밀번호 등 모든 구성을 포함하는 파일입니다.

워크플로우에 따라 Git에서 제외하고 싶을 수 있습니다. 예를 들어 프로젝트가 공개된 경우입니다. 이 경우 프로젝트를 빌드하거나 배포하는 동안 CI 도구가 이를 얻을 수 있는 방법을 설정해야 합니다.

한 가지 방법은 각 환경 변수를 CI/CD 시스템에 추가하고 `.env` 파일을 읽는 대신 해당 특정 환경 변수를 읽도록 `docker-compose.yml` 파일을 업데이트하는 것입니다.

## Pre-commit 및 코드 린팅

코드 린팅 및 포맷팅을 위해 [pre-commit](https://pre-commit.com/)이라는 도구를 사용하고 있습니다.

설치하면 git에서 커밋하기 직전에 실행됩니다. 이렇게 하면 코드가 커밋되기 전에도 일관되고 포맷팅되도록 보장합니다.

프로젝트 루트에 구성이 포함된 `.pre-commit-config.yaml` 파일을 찾을 수 있습니다.

#### 자동으로 실행되도록 pre-commit 설치

`pre-commit`은 이미 프로젝트의 종속성 중 하나이지만 원하는 경우 전역적으로 설치할 수도 있습니다. [공식 pre-commit 문서](https://pre-commit.com/)를 따르세요.

`pre-commit` 도구를 설치하고 사용 가능한 후에는 각 커밋 전에 자동으로 실행되도록 로컬 저장소에 "설치"해야 합니다.

`uv`를 사용하면 다음과 같이 할 수 있습니다:

```bash
❯ uv run pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

이제 커밋을 시도할 때마다, 예:

```bash
git commit
```

...pre-commit이 실행되어 커밋하려는 코드를 확인하고 포맷팅하며, 해당 코드를 다시 git에 추가(스테이징)하도록 요청합니다.

그런 다음 수정/변경된 파일을 다시 `git add`하고 이제 커밋할 수 있습니다.

#### 수동으로 pre-commit 훅 실행

모든 파일에 대해 `pre-commit`을 수동으로 실행할 수도 있습니다. `uv`를 사용하면 다음과 같이 할 수 있습니다:

```bash
❯ uv run pre-commit run --all-files
check for added large files..............................................Passed
check toml...............................................................Passed
check yaml...............................................................Passed
ruff.....................................................................Passed
ruff-format..............................................................Passed
eslint...................................................................Passed
prettier.................................................................Passed
```

## URL

프로덕션 또는 스테이징 URL은 동일한 경로를 사용하지만 자신의 도메인을 사용합니다.

### 개발 URL

로컬 개발용 개발 URL입니다.

프론트엔드: http://localhost:5173

백엔드: http://localhost:8000

자동 인터랙티브 문서 (Swagger UI): http://localhost:8000/docs

자동 대체 문서 (ReDoc): http://localhost:8000/redoc

Adminer: http://localhost:8080

Traefik UI: http://localhost:8090

MailCatcher: http://localhost:1080

### `localhost.tiangolo.com` 구성이 적용된 개발 URL

로컬 개발용 개발 URL입니다.

프론트엔드: http://dashboard.localhost.tiangolo.com

백엔드: http://api.localhost.tiangolo.com

자동 인터랙티브 문서 (Swagger UI): http://api.localhost.tiangolo.com/docs

자동 대체 문서 (ReDoc): http://api.localhost.tiangolo.com/redoc

Adminer: http://localhost.tiangolo.com:8080

Traefik UI: http://localhost.tiangolo.com:8090

MailCatcher: http://localhost.tiangolo.com:1080
