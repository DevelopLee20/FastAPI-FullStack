# FastAPI 프로젝트 - 프론트엔드

프론트엔드는 [Vite](https://vitejs.dev/), [React](https://reactjs.org/), [TypeScript](https://www.typescriptlang.org/), [TanStack Query](https://tanstack.com/query), [TanStack Router](https://tanstack.com/router), [Chakra UI](https://chakra-ui.com/)로 빌드되었습니다.

## 프론트엔드 개발

시작하기 전에 시스템에 Node Version Manager (nvm) 또는 Fast Node Manager (fnm)가 설치되어 있는지 확인하세요.

* fnm을 설치하려면 [공식 fnm 가이드](https://github.com/Schniz/fnm#installation)를 따르세요. nvm을 선호한다면 [공식 nvm 가이드](https://github.com/nvm-sh/nvm#installing-and-updating)를 사용하여 설치할 수 있습니다.

* nvm 또는 fnm을 설치한 후 `frontend` 디렉토리로 이동합니다:

```bash
cd frontend
```

* `.nvmrc` 파일에 지정된 Node.js 버전이 시스템에 설치되어 있지 않은 경우 적절한 명령어를 사용하여 설치할 수 있습니다:

```bash
# fnm을 사용하는 경우
fnm install

# nvm을 사용하는 경우
nvm install
```

* 설치가 완료되면 설치된 버전으로 전환합니다:

```bash
# fnm을 사용하는 경우
fnm use

# nvm을 사용하는 경우
nvm use
```

* `frontend` 디렉토리 내에서 필요한 NPM 패키지를 설치합니다:

```bash
npm install
```

* 다음 `npm` 스크립트로 라이브 서버를 시작합니다:

```bash
npm run dev
```

* 그런 다음 브라우저에서 http://localhost:5173/을 엽니다.

이 라이브 서버는 Docker 내에서 실행되지 않으며 로컬 개발용이며, 이것이 권장되는 워크플로우입니다. 프론트엔드에 만족하면 프론트엔드 Docker 이미지를 빌드하고 시작하여 프로덕션과 유사한 환경에서 테스트할 수 있습니다. 하지만 변경할 때마다 이미지를 빌드하는 것은 라이브 리로드가 있는 로컬 개발 서버를 실행하는 것만큼 생산적이지 않습니다.

다른 사용 가능한 옵션을 보려면 `package.json` 파일을 확인하세요.

### 프론트엔드 제거

API 전용 앱을 개발 중이고 프론트엔드를 제거하려는 경우 쉽게 할 수 있습니다:

* `./frontend` 디렉토리를 제거합니다.

* `docker-compose.yml` 파일에서 전체 서비스/섹션 `frontend`를 제거합니다.

* `docker-compose.override.yml` 파일에서 전체 서비스/섹션 `frontend`와 `playwright`를 제거합니다.

완료되었습니다. 프론트엔드가 없는(API 전용) 앱이 생겼습니다. 🤓

---

원하는 경우 다음에서 `FRONTEND` 환경 변수도 제거할 수 있습니다:

* `.env`
* `./scripts/*.sh`

하지만 이것은 정리하기 위한 것일 뿐이며, 그대로 두어도 실제로는 아무런 영향이 없습니다.

## 클라이언트 생성

### 자동으로

* 백엔드 가상 환경을 활성화합니다.
* 최상위 프로젝트 디렉토리에서 스크립트를 실행합니다:

```bash
./scripts/generate-client.sh
```

* 변경사항을 커밋합니다.

### 수동으로

* Docker Compose 스택을 시작합니다.

* `http://localhost/api/v1/openapi.json`에서 OpenAPI JSON 파일을 다운로드하고 `frontend` 디렉토리의 루트에 새 파일 `openapi.json`으로 복사합니다.

* 프론트엔드 클라이언트를 생성하려면 다음을 실행합니다:

```bash
npm run generate-client
```

* 변경사항을 커밋합니다.

백엔드가 변경될 때마다(OpenAPI 스키마 변경) 이 단계를 다시 따라 프론트엔드 클라이언트를 업데이트해야 합니다.

## 원격 API 사용

원격 API를 사용하려면 환경 변수 `VITE_API_URL`을 원격 API의 URL로 설정할 수 있습니다. 예를 들어 `frontend/.env` 파일에서 설정할 수 있습니다:

```env
VITE_API_URL=https://api.my-domain.example.com
```

그러면 프론트엔드를 실행할 때 해당 URL을 API의 기본 URL로 사용합니다.

## 코드 구조

프론트엔드 코드는 다음과 같이 구성됩니다:

* `frontend/src` - 메인 프론트엔드 코드
* `frontend/src/assets` - 정적 자산
* `frontend/src/client` - 생성된 OpenAPI 클라이언트
* `frontend/src/components` - 프론트엔드의 다양한 컴포넌트
* `frontend/src/hooks` - 커스텀 훅
* `frontend/src/routes` - 페이지를 포함하는 프론트엔드의 다양한 라우트
* `theme.tsx` - Chakra UI 커스텀 테마

## Playwright를 사용한 End-to-End 테스팅

프론트엔드에는 Playwright를 사용한 초기 end-to-end 테스트가 포함되어 있습니다. 테스트를 실행하려면 Docker Compose 스택이 실행 중이어야 합니다. 다음 명령어로 스택을 시작합니다:

```bash
docker compose up -d --wait backend
```

그런 다음 다음 명령어로 테스트를 실행할 수 있습니다:

```bash
npx playwright test
```

UI 모드에서 테스트를 실행하여 브라우저를 보고 상호 작용할 수도 있습니다:

```bash
npx playwright test --ui
```

Docker Compose 스택을 중지하고 제거하며 테스트에서 생성된 데이터를 정리하려면 다음 명령어를 사용합니다:

```bash
docker compose down -v
```

테스트를 업데이트하려면 tests 디렉토리로 이동하여 기존 테스트 파일을 수정하거나 필요에 따라 새 파일을 추가합니다.

Playwright 테스트 작성 및 실행에 대한 자세한 내용은 공식 [Playwright 문서](https://playwright.dev/docs/intro)를 참조하세요.
