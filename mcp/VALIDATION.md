# 로컬 검증 기록

외부 사이트의 유효성 검증이나 원격 배포 증거가 아닙니다. 기존 작업 브랜치 `feat/read-only-mcp`에서 리뷰 수정을 수행했습니다. commit/push/npm publish/배포는 실행하지 않았습니다.

## 리뷰 회귀 TDD: RED → GREEN

구현 변경 전에 `test/core.test.js`, `test/integration.test.js`에 회귀 검사를 먼저 추가했습니다.

- 첫 RED `npm test`: 10개 중 pass 5 / fail 5. 원문 `학습` 검색 실패, $가 `paid`로 반환됨, 미지원 사이트 문법이 오류 없이 누락되거나 `Empty extraction`으로만 실패, rate exhaustion 후 health 429, packed README 설치자 안내 없음.
- 누락 사이트를 더 정확히 재현하도록 유효한 사이트 뒤에 미지원 사이트를 배치하고, 번호/탭/별도 목록 마커·alias 중복·환경값 검사를 독립 테스트로 분리했습니다.
- 두 번째 RED `npm test`: 19개 중 pass 6 / fail 13. 탭, `1.`, `1)`, `*`, `+`, 마커 없는 외부 링크는 각각 `Missing expected exception`; 빈 alias로 기존 ID를 다시 사용하는 경우도 누락. `readRateConfig` 미구현 및 잘못된 numeric budget 무검증을 확인했습니다. 원본 RED 로그는 실행 환경의 `/tmp/site-review-red.log`에 남겼습니다(임시 파일, 배포물 아님).
- 기존 코드가 이미 거부하던 primary/alias 충돌 1개는 RED 단계에서도 통과했으며, 이 검사는 추가 보호 검사입니다.
- 구현 수정과 catalog 재생성 후 GREEN: Node 25.8.1에서 **19/19**, Node 22.23.3에서 **19/19**. 취소/skip 없음.

## 수정 계약과 실제 검증 범위

1. 설명의 학습/튜토리얼/게임 원문은 유지하고 실습 alias를 추가합니다. `학습` + category `regex` → Regex101, `깃 실습` → Learn Git Branching 모두 확인. `matchedFields`는 alias가 나온 원래 필드이며 literal-only라는 주장을 하지 않습니다.
2. distinct 원본 `rawLabels`를 URL 중복 전체에서 최초 순서로 병합. $만 있으면 `paid-or-freemium`(유료/부분유료), F+$는 `free-and-paid`. 실제 catalog 전체가 parser 출력과 동일함을 검사합니다.
3. 링크 섹션의 미지원 목록/외부 사이트 구문은 생성 실패. 모든 span ID의 중복 검사에 빈 alias 포함. 현재 원본 통계는 그대로 entries 376 / uniqueSites 370 / categoryCount 57.
4. archive README 자체에 설치 사용자와 저장소 개발자 안내를 분리하고 HTTP/stdio, 환경값·보안·스냅샷 한계를 포함합니다. 통합 테스트는 `npm pack` 후 **저장소 밖 새 임시 디렉터리에서 실제 `npm install <생성된 tgz> --ignore-scripts --no-audit --no-fund`**를 실행합니다. 설치된 `.bin/site-for-developers-mcp --stdio`를 실제 SDK 클라이언트로 초기화, tools/list 및 세 도구 호출, schema 위반/없는 ID/검색 0건까지 검사합니다. 저장소 node_modules symlink는 사용하지 않습니다. bin shebang PATH의 첫 항목을 테스트 Node 실행 파일 디렉터리로 설정해 Node 22 검사 시 bin도 Node 22를 사용합니다. 설치에는 registry/cache 의존성 확보가 필요하며 완전 오프라인 설치라는 주장은 하지 않습니다.
5. query budget exhaustion 뒤 `/health`가 반복 200이며 forwarding header 변경으로 query 제한을 우회하지 못함을 검사합니다. `MCP_MAX_REQUESTS` 기본 120/범위 1–100000, `MCP_RATE_WINDOW_MS` 기본 60000/범위 1–3600000, 잘못된 형식·빈 문자열·0·음수·분수·비유한·범위초과 값을 거부합니다. 환경 reader와 HTTP factory 모두 검사. Host/Origin, 405, malformed JSON/RPC, 64 KiB 한도 등 기존 hostile HTTP 검사도 통과합니다.

## 실행 명령 및 관측

`mcp/`에서 이번 리뷰 수정 후 실행:

```sh
npm ci --ignore-scripts
npm run catalog:generate
npm run catalog:check
npm test
npm exec --yes --package=node@22 -- node --version
npm exec --yes --package=node@22 -- node --test test/*.test.js
npm audit --omit=dev
npm pack --json
git diff --check
```

- `npm ci`: 94 packages 설치, 95 packages audit, 0 vulnerabilities.
- generate/check: 모두 성공, `{entries:376,uniqueSites:370,categoryCount:57}`.
- 기본 Node v25.8.1 및 Node v22.23.3: 각각 19 pass / 0 fail.
- `npm audit --omit=dev`: found 0 vulnerabilities (실행 시점 advisory 결과이며 영구 보장 아님).
- `npm pack --json`: `site-for-developers-mcp-0.1.0.tgz`, 9개 파일. README, catalog, 실행 가능한 bin, 소스, package manifest, LICENSE 포함. 개발용 lockfile/test/scripts는 의도적으로 제외하고 README는 저장소 개발용 명령을 설치 사용자에게 요구하지 않습니다.
- stale README 및 invalid README를 대상으로 catalog check가 실패하는 것도 통합 테스트로 확인.
- `git diff --check`: 성공. 기존 branch 유지.

초기 구현 기록(이번 리뷰 수정 이전): missing-module RED 후 7/7 테스트, Docker 로컬 이미지 빌드 성공이 기록되어 있었습니다. **이번 수정에서는 Docker 재빌드/실행 또는 배포를 수행하지 않았습니다.** 위 19/19 및 실제 설치 검증이 현재 코드의 검증 근거입니다.

## 운영 한계 / 남은 작업

실제 DNS/TLS, gateway 인증/접근 제어, allowlist, 측정 기반 예산, 모니터링/재시작, 스냅샷 갱신 책임자는 운영자가 정해야 합니다. backend는 socket-IP별 제한이며 단일 reverse proxy 뒤에서는 전체 사용자가 같은 **공유 안전 예산**을 씁니다. gateway 사용자별 제한은 그 공유 병목을 없애지 않습니다. backend 예산을 전체 요청량에 맞게 설정하고 gateway 합산 cap을 여유 있게 그 아래로 제한하며 별도 사용자 quota를 둡니다. 여러 proxy/프로세스 간 분산 전체 제한은 제공하지 않습니다. Forwarded/X-Forwarded-* 신뢰를 추가하지 않았습니다. health 200은 query 여유·외부 링크 검증 증거가 아니므로 backend 429도 모니터링해야 합니다. 실제 부하/TLS/인증 검증, 브라우저 CORS, 세션 재개, 외부 링크/가격 검증 및 자동 최신화는 범위 밖입니다.
