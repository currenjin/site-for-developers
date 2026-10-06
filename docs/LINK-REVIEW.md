# 링크 검토 기록

## 범위와 확인 한계

2026-10-06 전체 링크 감사와 수정 단계의 추가 확인을 바탕으로 작성했습니다. 사이트 목록은 README.md에서만 관리하며, 이 문서는 교체·제외 이유와 보류한 사항을 기록합니다.

변경한 문서 진입점은 HTTP 응답, 최종 리디렉션과 문서 내용을 확인했습니다. HTTP 200은 자료 품질이나 모든 기능의 동작을 보장하지 않습니다. 전체 서비스의 가격·라이선스·개인정보 처리와 실제 기능을 전수 검증한 것은 아닙니다.

HTTP 403·429, DNS 실패, HTTP 404, TLS 핸드셰이크·인증서 오류를 구분합니다. 차단이나 한 환경의 접속 실패만으로 서비스 전체 종료를 단정하지 않습니다.

## 교체·통합 및 라벨 정정

| 대상 | 확인한 상태 / 적용 내용 | 공개 근거 |
| --- | --- | --- |
| Windsurf / Codeium | `www.windsurf.io` DNS 실패. 공식 Windsurf·Codeium 입구는 Devin Desktop으로 이동하며 FAQ가 Windsurf의 새 이름으로 설명. 데스크톱 항목 통합. 별도 플러그인의 현행 제공 여부는 미확인 | [Devin Desktop](https://devin.ai/desktop) |
| Stripe | `/kr`는 404, 공식 루트는 200. 루트로 교체 | [Stripe](https://stripe.com) |
| Ktlint | 기존 Pinterest 문서 경로는 404. 현행 프로젝트의 `latest/` 문서는 200이며 Kotlin 린터 문서임을 확인 | [프로젝트](https://github.com/ktlint/ktlint), [문서](https://ktlint.github.io/ktlint/latest/) |
| React | 기존 입구는 업데이트가 중단된 18.2 구문서로 이동. 현행 한국어 공식 문서로 교체 | [현행 문서](https://ko.react.dev), [구문서](https://ko.legacy.reactjs.org/) |
| Django | 5.0은 지원 종료 버전. 지원되는 안정 버전의 공식 입문 문서로 교체 | [지원 표](https://www.djangoproject.com/download/), [안정 버전 문서](https://docs.djangoproject.com/ko/stable/intro/) |
| Flask | 기존 한국어 번역은 0.11-dev. 안정 버전 공식 문서로 교체하고 언어를 EN으로 수정 | [공식 문서](https://flask.palletsprojects.com/en/stable/), [구번역](https://flask-docs-kr.readthedocs.io/ko/latest/) |
| GraphQL | 한국어 페이지의 저장소에서 번역 기여를 안내. 공식 영어 문서와 커뮤니티 번역을 분리 | [공식 문서](https://graphql.org/learn/), [번역 저장소](https://github.com/graphql-kr/graphql-kr.github.io) |
| Flutter | 한국어 경로는 리디렉션 안내·간헐적 연결 실패로 내용 확인이 제한됨. 정상 접속되는 현행 공식 영어 문서로 교체. 한국어 사이트 종료를 단정하지 않음 | [공식 문서](https://docs.flutter.dev/) |
| CentOS | 위키 자체가 읽기 전용 아카이브라고 명시. 현행 제품 문서로 소개하지 않고 아카이브로 표시 | [아카이브](https://wiki.centos.org/) |
| Ubuntu | 한국 지역 커뮤니티를 공식 제품 문서와 구분. 커뮤니티는 유지하고 공식 서버 문서를 별도로 제공 | [커뮤니티](https://ubuntu-kr.org), [서버 문서](https://ubuntu.com/server/docs) |
| CodeWhisperer | 공식 입구가 Amazon Q Developer로 이동. 공식 페이지의 IDE 플러그인 지원 종료 예정일은 2027-04-30. 서비스 전체 종료로 표현하지 않음 | [Amazon Q Developer](https://aws.amazon.com/q/developer/) |
| Claude Code | 설치 문서는 유료 Claude 플랜 또는 Console 계정 등이 필요하고 무료 claude.ai 플랜에는 포함되지 않는다고 명시. `F` 제거 | [계정 요구사항](https://code.claude.com/docs/en/setup) |
| PlanetScale | 무료 Hobby는 2024-04-08 종료. `F` 제거. 현행 Postgres·Vitess/MySQL 제품 설명 반영 | [Hobby 종료 공지](https://planetscale.com/blog/planetscale-forever), [가격·제품](https://planetscale.com/pricing) |
| n8n | Sustainable Use License의 제한적 소스 공개를 OSI 오픈소스로 표시하지 않음. 셀프호스팅과 유료 Cloud를 구분 | [라이선스 원문](https://github.com/n8n-io/n8n/blob/master/LICENSE.md) |
| Cursor / GitHub Copilot | 공식 사이트의 무료·유료 플랜 구분을 반영. Cursor는 공식 입구로 통일하고 IDE 목록의 중복은 내부 참조로 전환 | [Cursor 요금](https://cursor.com/pricing), [Copilot 플랜](https://docs.github.com/en/copilot/get-started/plans) |
| JUnit | 기존 JUnit 5 링크는 JUnit 6.1.3 문서로 이동. 버전 고정 이름과 구 앵커를 제거하고 현행 공식 진입점으로 교체. 백엔드 프레임워크에서 테스트 도구로 이동 | [현행 가이드](https://docs.junit.org/current/user-guide/) |
| DataSpell | 한국어·영어 공식 입구가 PyCharm의 데이터 과학 페이지로 이동. 별도 신규 추천 항목은 제거하고 PyCharm 설명에 데이터 과학 기능 반영 | [최종 공식 입구](https://www.jetbrains.com/pycharm/data-science/) |
| 안영회 습작 | 기존 URL은 단일 글. 작성자 글 목록 진입점은 200이며 페이지 제목이 해당 작성자임을 확인 | [작성자 글 목록](https://brunch.co.kr/@graypool) |

## 신규 추천에서 제외 / 링크 제거

- **Fleet**: 공식 공지가 2025-12-22 이후 다운로드 제공 중단과 추가 업데이트 중단을 설명하므로 신규 IDE 목록에서 제외했습니다. [공식 공지](https://blog.jetbrains.com/fleet/2025/12/the-future-of-fleet/)
- **프로그래머스 QnA** (`qna.programmers.co.kr`): DNS 실패, 현행 공식 대체 경로를 확보하지 못해 해당 링크만 제거했습니다. 코딩테스트 항목은 유지하며 브랜드 전체 종료를 뜻하지 않습니다.
- **매일메일** (`www.maeil-mail.kr`, 루트 도메인도 DNS 실패): 현행 대체 경로를 확보하지 못해 해당 링크만 제거했습니다. 브랜드 전체 종료는 미확인입니다.
- **Enfax / xdiarys**: 일반 팩스·일정 관리 설명만으로 개발에서의 직접 사용 가치를 확인하기 어려워 제외했습니다. 접속 실패나 서비스 종료가 이유는 아닙니다.

## 분류·중복·설명 정비

- 일반 배포·DB·인증·결제·이메일 인프라는 AI 하위에서 일반 개발 도구로 이동했습니다. 기존 `ai-infra` 앵커는 호환용으로 유지합니다.
- Node.js는 런타임으로, DSH Studio 등은 코딩 에이전트 관리 도구로 분리했습니다. 로컬 관리 앱과 로컬 모델 실행을 혼동하지 않습니다.
- Android Studio는 Google이 배포하는 IntelliJ 플랫폼 기반 IDE로 정정했습니다. URL 인코딩 도구는 IDE에서 개발 보조 도구로 이동했습니다.
- Udemy·부스트코스·TCP School·Poiemaweb·CodeCrafters·Learn Git Branching·더북·K-MOOC는 학습에 통합했습니다. Express·NestJS는 백엔드 문서에, Hugging Face는 모델·API에 기본 항목을 둡니다. 추천 재노출과 내부 참조는 유지합니다.
- 목차 누락, 잘린 문장, 번역 오류, 근거 없는 순위·광고 문구를 정리했습니다. 개인 블로그와 저장소 소유자의 아카이브도 같은 편집 기준을 적용합니다.

## 기능·정책의 확인 범위

- **All Tools Verse / A Box of Tools / Nutilz**: 각 홈페이지가 무료 도구임을 명시하므로 `F`를 유지했습니다. 도구 수는 변경되기 쉬워 설명에서 제거했습니다. 홈페이지의 주장을 모든 기능에 대한 독립 보안 검증으로 취급하지 않습니다.
- **A Box of Tools**: 홈페이지와 [공개 코드 라이선스](https://github.com/A-Box-of-Tools/website/blob/main/LICENSE)의 MIT 표기를 근거로 `O`를 유지했습니다. 콘텐츠 라이선스는 코드와 별개입니다.
- **Nutilz**: 홈페이지가 일부 음성·오디오 도구를 서버 처리로 설명하므로 사이트 전체가 클라이언트에서만 실행된다는 문구는 제거했습니다.
- **AI Router**: 제3자 OpenAI 호환 게이트웨이라는 기능 설명을 유지했습니다. 키 종류와 운영·데이터 저장·전송·보존 정책은 추가 확인 대상이며 안전하지 않다고 단정하지 않습니다.
- **기타 비용·라이선스 라벨**: 확인된 오류를 정정했으며 모든 기존 라벨을 재검증한 것은 아닙니다. 외부 모델·API·호스팅 비용은 별도일 수 있습니다.

## 유지하고 재확인할 접속 문제

| 대상 | 보류 이유 / 다음 확인 사항 |
| --- | --- |
| [HTML DOM](https://phuoc.ng/collection/html-dom) | 반복 TLS 핸드셰이크 실패. 자료 삭제가 확인된 것은 아니므로 유지. 다른 신뢰 가능한 네트워크·TLS 환경에서 재확인 |
| [DGM](https://dgm.sh/home) | 인증서 검증 실패. 서버와 클라이언트 신뢰 체인의 원인을 구분하지 못했으므로 유지. 인증서 검증 해제를 사용법으로 안내하지 않음 |
| [GitHub stargazers](https://github.com/currenjin/site-for-developers/stargazers) | 감사 시 웹 GET 404와 GitHub API의 정상 별 수 집계가 충돌하므로 삭제하지 않음 |
| 기타 HTTP 403·429 | 봇 차단·접속 제한일 수 있으므로 삭제 근거로 사용하지 않음. 필요하면 일반 브라우저에서 개별 확인 |
