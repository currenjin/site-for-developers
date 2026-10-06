# 읽기 전용 MCP

README.md가 사이트 목록의 유일한 원본입니다. `mcp/catalog.json`은 그 원본으로부터 결정적으로 생성한 **번들 스냅샷**이며 별도 편집하지 않습니다. 서버는 시작 시 번들만 읽습니다. 사이트 URL·사용자 파일을 읽거나 웹 요청, LLM 호출, 데이터 변경을 하지 않습니다.

## 1. 기본 연결: 원격 Streamable HTTP

아직 공개 엔드포인트나 npm 배포는 없습니다. 다음 주소는 **로컬 smoke 전용**입니다.

```sh
cd mcp
npm ci --ignore-scripts
npm run catalog:check
npm test
npm start
# http://127.0.0.1:3000/mcp  (MCP 클라이언트의 Streamable HTTP URL)
curl http://127.0.0.1:3000/health
```

MCP SDK의 stateless Streamable HTTP를 사용합니다. 각 POST는 별도 서버/transport이며 세션 ID와 재개 이벤트 저장소가 없습니다. `GET /mcp`의 SSE 구독과 `DELETE /mcp`의 세션 종료는 지원하지 않아 JSON-RPC 오류와 405를 반환합니다. 그 밖의 메서드도 405이며 `Allow: POST`를 제공합니다. MCP 초기화·알림·프로토콜 버전·Accept 검증은 공식 SDK가 처리합니다. POST JSON 본문은 최대 64 KiB, 요청/헤더 타임아웃은 10초입니다.

### 외부 배포 전 필수 준비

- 실제 운영 DNS와 TLS 인증서, reverse proxy 또는 플랫폼을 직접 준비해야 합니다. 이 문서는 배포나 계정·자격증명을 만들지 않습니다.
- 기본 bind는 `127.0.0.1`입니다. 외부 bind에는 **둘 다 명시**해야 합니다: `MCP_ALLOWED_HOSTS`(쉼표로 구분한 소문자 host 이름, 포트 제외), `MCP_ALLOWED_ORIGINS`(스킴·호스트·포트가 일치하는 실제 Origin). `*`는 금지합니다. Origin 없는 네이티브 클라이언트는 허용하되 Host는 항상 검증합니다.
- proxy는 검증할 실제 Host를 보존/설정해야 합니다. 서버는 `Forwarded`/`X-Forwarded-*`를 신뢰하지 않습니다. Origin은 인증 수단이 아니므로 원격 서비스 정책에 맞춰 proxy에서 인증·접근 제어를 추가하세요.
- CORS 허용 헤더/프리플라이트를 제공하지 않습니다. 브라우저 직접 연결이 필요하면 검토된 동일 출처 gateway를 별도로 설계해야 합니다.
- 기본은 프로세스별 원격 socket IP당 60초에 `/mcp` 120회 제한(429 + Retry-After), 최대 10,000개 활성 버킷입니다. `GET /health`는 이 제한을 소비하거나 차단되지 않지만 Host/Origin 검증은 유지합니다. `MCP_MAX_REQUESTS`(정수 1–100000, 기본 120), `MCP_RATE_WINDOW_MS`(정수 1–3600000 ms, 기본 60000)를 명시적으로 설정할 수 있으며 잘못된 값은 시작 실패입니다.
- proxy 뒤에서는 모든 사용자가 같은 backend socket IP 버킷을 공유하므로 기본 120회는 **사용자별이 아니라 합산 한도**입니다. gateway 사용자별 제한만으로 이 병목이 해결되지 않습니다. backend 한도는 측정한 전체 부하에 맞춘 공유 안전 예산으로 설정하고 gateway에는 별도의 사용자별 제한과 backend 예산보다 낮은 합산 제한(초기화/알림/버스트 여유 포함)을 적용하세요. 예: backend 6000회/60000 ms, gateway 합산 5000회/분 + 사용자별 별도 quota. 예시 값은 처리량 보장이 아니며 실제 부하 검증이 필요합니다. 여러 proxy/프로세스는 별도 버킷이므로 분산 전체 제한도 아닙니다. 직접 backend 접근을 차단하고 연결/동시성·본문 크기·타임아웃 제한도 적용하세요. forwarding 헤더를 신뢰하는 우회는 없으며 완전한 DoS 방어의 대체가 아닙니다.
- 모니터링, 재시작, 인증, 로그 보존 정책, 취약점 재점검, 스냅샷 갱신 책임자를 지정하세요. `/health`는 생존 확인이지 외부 링크 검증이 아닙니다.

Docker build context는 저장소 루트입니다.

```sh
docker build -f mcp/Dockerfile -t site-for-developers-mcp .
# 실제 HOST/ORIGIN 값으로 교체한 뒤만 실행합니다. 공개 배포 예제가 아닙니다.
# 컨테이너 bind에는 명시적 allowlist가 필수입니다.
```

컨테이너는 non-root Node 22, 포트 3000이며 TLS/인증은 포함하지 않습니다. Docker 실행 시 `MCP_ALLOWED_HOSTS`, `MCP_ALLOWED_ORIGINS`를 실제 환경에 맞게 전달해야 합니다. 비밀을 이미지에 넣지 않습니다.

## 2. 대안: 로컬 stdio

Node.js 22 이상이 필요합니다. 공개 npm 패키지 이름으로 `npx` 실행하는 안내는 하지 않습니다.

```sh
cd mcp
npm ci --ignore-scripts
npm pack
# 생성된 .tgz의 실제 절대 경로를 사용해 로컬 프로젝트에 설치
npm install /absolute/path/to/site-for-developers-mcp-0.1.0.tgz --ignore-scripts
# 클라이언트 설정: command = node
# args = ["/absolute/path/to/node_modules/site-for-developers-mcp/src/cli.js", "--stdio"]
```

설치된 bin `site-for-developers-mcp`도 같은 stdio를 실행합니다. 작업 디렉터리와 README 위치에 의존하지 않습니다. stdout은 MCP 전용입니다. npm 설치에는 의존성 확보가 필요하며 실행 시에는 원본 README나 네트워크가 필요하지 않습니다. 자동 테스트는 `npm pack` 후 저장소 밖 새 임시 디렉터리에서 실제 `npm install <archive> --ignore-scripts`를 실행하고 설치된 `node_modules/.bin/site-for-developers-mcp`를 SDK stdio 클라이언트로 초기화/도구 호출합니다. 로컬 의존성 symlink를 사용하지 않습니다. 설치에는 registry/cache가 필요할 수 있습니다. 설치 사용자에게 필요한 독립적인 HTTP/stdio·보안·스냅샷 안내는 archive의 README에 포함합니다. `npm ci`/`npm test`/생성 명령은 lockfile·테스트·스크립트가 있는 저장소 개발자 전용입니다.

## 도구와 데이터 계약

모든 도구는 readOnly/idempotent, non-destructive, closed-world annotation을 가집니다.

- `search_sites`: `query` 선택, 최대 200자. `category` 선택(카테고리 ID), `language` 선택(`KR`/`EN`), `limit` 정수 1–20, 기본 10. 알 수 없는 필드·타입·범위는 오류입니다. 없는 카테고리는 결과 0개입니다.
- `get_site`: 안정적인 `site_` ID. 없는 ID는 `isError` 결과입니다.
- `list_categories`: 카테고리 ID·이름·부모·중복 병합된 사이트 수입니다. 상위 분류에도 사이트가 포함됩니다.

검색은 대소문자 무시 AND 키워드 매칭입니다. `깃 ↔ git`, `레디스 ↔ redis`, `정규식/정규표현식/regular expression ↔ regex`, `연습/practice/exercise ↔ 실습`을 정규화합니다. 설명 내 학습·튜토리얼·게임 원문을 보존하면서 실습 별칭을 추가합니다. 예: `깃 실습`, `학습` + category `regex`, `레디스`, `정규표현식`. 의미 검색이나 LLM 추천은 아닙니다. 안정적인 ID 순서로 반환하며 `matchedFields`는 이름·설명·URL·카테고리 중 원문 또는 문서화된 별칭이 매칭된 원래 필드를 설명합니다(항상 literal substring이라는 뜻은 아닙니다). 추정 점수/순위를 만들지 않습니다. 빈 질의는 `filters`로 표시합니다. `total`은 제한 전 매칭 수입니다.

URL은 URL 표준의 정규화(루트 `/` 등) 후 SHA-256 앞 24자리로 ID를 만듭니다. URL 변경은 ID 변경입니다. query/fragment는 보존하며 리디렉션·서로 다른 URL의 동일 서비스 여부는 추정하지 않습니다. 중복 URL의 분류·라벨은 합치고 이름·설명은 첫 항목을 유지합니다. `<span id>` 들여쓰기 계층을 보존합니다. 이름이 명시된 `[Cursor](#ai-dev-tools)`만 해당 사이트의 추가 분류로 병합하고, 일반 카테고리 안내는 링크를 검증하되 전체 사이트 분류를 복제하지 않습니다. 목차/이미지/기여자/라이선스 링크는 제외합니다.

`rawLabels`는 중복 URL 전체에서 원본 라벨을 처음 나온 순서대로 중복 없이 보존합니다. `languages`는 README의 EN/KR 라벨만 반영하며 미기재는 빈 배열입니다. `cost`는 F → `free`, $만 있으면 README의 유료/부분유료 의미를 보존한 `paid-or-freemium`, F+$ → `free-and-paid`, 미기재 → `unknown`; 무료/유료 여부를 추가 추정하지 않습니다. `openSource`는 O 라벨 존재 여부이지 라이선스 검증이 아닙니다. `source.url`, `source.version`(README 바이트의 SHA-256), `verified:false`는 **출처/버전이지 접속·가격·언어·라이선스 검증 증거가 아닙니다**. 운영 시 공식 사이트를 다시 확인하세요.

## 갱신과 검증

번들은 자동으로 최신화되지 않습니다. README 변경 후 다음을 실행하고 생성된 JSON을 함께 리뷰해야 합니다. 배포된 이미지/로컬 패키지를 다시 만들고 교체하기 전에는 이전 목록을 계속 제공합니다.

```sh
cd mcp
npm run catalog:generate
npm run catalog:check
npm test
npm audit --omit=dev
npm pack
cd ..
git diff --check
```

파서는 현재 README의 공백 들여쓰기 `- ` 목록 문법의 명시적인 변환기이며 범용 Markdown 렌더러가 아닙니다. 문법 변경 시 테스트와 파서를 함께 업데이트하세요. 누락 섹션, 탭 들여쓰기·번호 목록 등 미지원 목록/외부 사이트 문법, 빈 alias를 포함한 모든 중복 span ID, 비정상 사이트 링크/메타데이터, 미해결 앵커는 조용히 누락하지 않고 생성 실패입니다. CI는 관련 경로 변경에만 설치·생성 일치 검사·테스트·runtime audit를 실행하고 발행/배포하지 않습니다.
