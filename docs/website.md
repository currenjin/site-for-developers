# 웹사이트

공개 주소: https://currenjin.github.io/site-for-developers/

## 원본과 생성물

리소스 목록의 정본은 저장소 루트 `README.md`다. 웹사이트용 목록을 따로 편집하지 않는다.

- `scripts/readme_catalog.py`: README의 `## 링크` 아래 목록을 파싱한다.
- `scripts/build_site.py`: README에서 JSON을 생성하고 허용한 웹 자산만 `_site/`에 복사한다.
- `web/`: 승인한 보석 랜딩, 검색·분류 UI, 로컬 3D 자산.
- `resources/icons/header_base/576x157/header_base.svg`: 기존 로고 원본. 빌드 시 그대로 복사한다.
- `favicon.svg`: 빌드 시 기존 로고의 보석 심볼만 추출해 정사각형 파비콘으로 생성한다. 워드마크와 헤더 로고는 바꾸지 않는다.
- `_site/`: 빌드 결과. Git에 넣지 않는다.

추천에서 재등장하는 자료는 원문과 같이 별도 항목으로 유지한다. `<sub>` 라벨이 없으면 미검증으로 남기며 가격·언어·라이선스를 추정하지 않는다. 웹 생성은 외부 링크의 현재 내용이나 가격을 다시 검사하는 작업이 아니다.

현재 파서는 이 저장소의 목록 형식을 지원한다. 분류 앵커, 들여쓰기, 링크, 라벨을 읽으며 지원하지 않는 외부 링크 행은 조용히 누락하지 않고 빌드를 실패시킨다. 분류 구조를 바꿀 때는 기존 내부 앵커 호환성과 테스트를 함께 확인한다.

## 로컬 빌드와 검증

Python 3.9 이상으로 빌드할 수 있다. 빌드에는 외부 패키지가 필요하지 않다.

```sh
python3 scripts/build_site.py
python3 -m unittest discover -s tests -p 'test_readme_catalog.py' -v
python3 -m unittest discover -s tests -p 'test_site_build.py' -v
```

브라우저 검증에는 Playwright가 필요하다. CI는 Playwright 1.58.0이 지원하는 Ubuntu 24.04와 아래 버전을 고정해 사용한다. `ubuntu-latest`가 새 OS로 이동해 브라우저 설치가 깨지는 일을 피한다.

```sh
python3 -m pip install playwright==1.58.0
python3 -m playwright install chromium
python3 -m unittest discover -s tests -p 'test_site_browser.py' -v
```

간단한 확인은 `_site/`에서 정적 서버를 열어 진행한다. `file://`로 여는 대신 HTTP를 사용한다. 브라우저 테스트는 실제 배포와 같은 `/site-for-developers/` 경로를 포함해 검사한다.

## 자동 배포

`.github/workflows/pages.yml`이 다음을 수행한다.

1. PR과 `main` 변경에서 전체 목록을 다시 생성하고 파서·출판 경계·브라우저 테스트를 실행한다.
2. PR은 검증만 한다. `main`의 검증이 성공하면 `_site/`만 GitHub Pages에 배포한다.
3. README가 변경되면 다음 배포 목록에 반영된다. 생성된 JSON이나 배포 브랜치를 수동 편집할 필요가 없다.

빌드 산출물에는 명시적인 허용 목록의 정적 파일만 포함된다. 소스 README, 테스트, 문서, CI 설정, 로컬 경로와 검토 기록은 사이트에 복사하지 않는다. 공개 저장소이므로 소스 자체는 GitHub에서 볼 수 있다.

## 3D와 검색

보석은 기존 로고 윤곽을 바탕으로 만든 스타일화된 3D 표현이며 로고 원본의 대체물이 아니다. 실제 광학을 계산하는 보석 시뮬레이터는 아니다. Three.js 사본과 MIT 라이선스를 `web/art/`에 함께 보존한다.

장면은 화면 밖에서 일시 정지한다. 동작 줄이기를 사용하거나 WebGL을 초기화할 수 없으면 정지 이미지를 표시한다. 외부 CDN, 글꼴, 모델 API 없이 로컬 자산으로 실행된다.

검색은 브라우저가 내려받은 목록 안에서 처리한다. 검색어와 분류는 공유 가능한 URL에 반영된다. 별도 검색 API, 사용자 계정, DB, 분석 도구는 없다. 외부 자료 링크를 열면 각 서비스로 이동한다.

## 한국어와 영어

- `/site-for-developers/`: 한국어 원본 화면.
- `/site-for-developers/en/`: 영어 화면. 로고·보석·파비콘·스타일은 공유한다.
- 언어 전환은 검색어, 분류와 URL 해시를 유지한다. 브라우저 언어로 강제 이동하지 않는다.
- `web/i18n/ui.json`: 한국어·영어 UI 문구. 목록 데이터가 아니라 버튼, 설명, 접근성 이름 등의 번역이다.
- `web/i18n/en.json`: README에서 추출한 원문 문자열을 키로 사용하는 영문 번역 캐시. 별도의 영문 리소스 목록이나 README를 관리하지 않는다.

이름·설명·분류명의 번역은 원문 문자열과 정확히 일치할 때만 재사용한다. 같은 설명이 추천과 다른 분류에 반복되면 번역은 공유하되 리소스 항목은 합치지 않는다. URL, 가격·언어 라벨, 분류 경로와 원본 식별자는 번역하지 않는다. 영문 화면에서도 KR/EN 라벨은 연결 대상의 원래 언어를 뜻한다.

### README를 수정한 다음

README 변경은 기존처럼 자동 빌드된다. 기존 문구는 캐시된 번역을 사용한다. 새로 추가되거나 바뀐 한국어 문구는 예전 번역을 재사용하지 않으며, 영문 화면에 한국어 원문과 번역 대기 표시로 먼저 반영한다. 번역 때문에 한국어 목록의 자동 갱신을 막지 않는다.

```sh
python3 scripts/translation_status.py
```

이 명령으로 현재 원문 중 번역이 필요한 문구를 확인하고 `web/i18n/en.json`에 해당 문구의 번역을 추가한다. 원문이 바뀐 키를 덮어쓰는 대신 새 원문 키에 맞는 번역을 작성한다. 다음 빌드에서 영어 설명과 대기 표시가 함께 갱신된다. 원문 필드·가격 조건·제품명을 바꾸거나 설명에 없는 주장을 더하지 않는다.

현재 구조는 번역 캐시와 변경분 탐지를 자동화한 것이며, 새 항목을 외부 모델 API로 자동 번역하는 구조는 아니다. 별도 API 키나 번역 서비스 비용이 없고, 변경된 설명의 영어 번역·검수만 추가하면 된다.

언어별 HTML의 `lang`, canonical, hreflang, 제목과 설명을 각각 생성한다. 검색은 번역된 표현과 원문을 함께 활용한다. 빌드 결과에는 양쪽 화면과 필요한 데이터만 포함하며 번역 작업용 소스 파일은 복사하지 않는다.

## GitHub Star 표시

상단 Star 버튼은 GitHub 저장소로 이동하는 링크이며, 방문자 대신 Star를 누르거나 로그인 상태를 읽지 않는다. 표시 숫자는 사용자 수가 아니라 GitHub Star 수다. `1.2k`처럼 압축 표시하고, 툴팁에는 확인한 정확한 수를 보여준다.

`scripts/github_stats.py`가 빌드 시 GitHub API에서 숫자를 확인한다. README 변경에 따른 배포 외에도 하루 한 번 예약 빌드로 갱신한다. 요청이 실패하면 `web/github.json`의 마지막 확인값을 유지하며 검색·목록 배포를 막지 않는다. 방문자 브라우저에서 외부 API를 호출하거나 인증 정보를 전달하지 않는다. `web/github.json`은 빌드 입력이며 배포 파일로 복사하지 않는다.

## 검색엔진 노출과 정적 목록

`static_render.py`는 같은 README 파싱·번역 결과에서 모든 리소스 카드를 두 언어의 초기 HTML에 생성한다. 검색엔진이나 JavaScript를 끈 브라우저도 실제 제목·설명·분류·라벨과 외부 `a[href]` 링크를 읽을 수 있다. 별도 편집 목록이나 검색엔진 전용 콘텐츠는 없다. 미번역 영어 필드는 한국어 원문과 `lang="ko"` 표시를 유지한다.

초기 리소스·분류 수는 생성 데이터 기준이다. JavaScript가 같은 카드를 확인하면 기존 DOM을 유지하고, 검색·분류 변경 시 목록을 교체한다. JSON 로딩 실패 시 정적 전체 목록과 링크는 남기되 검색·필터 실패를 안내한다. 검색·필터 자체는 JavaScript가 필요하다.

기존 `index,follow`, 언어별 canonical/hreflang, Open Graph, 파비콘과 두 URL의 sitemap을 유지한다. 검색어·분류 쿼리 URL도 해당 언어 루트를 canonical로 쓴다. 제목과 설명은 개발 리소스의 내용을 설명하며 항목 수나 Star 수를 넣지 않는다. `WebSite`·`CollectionPage` JSON-LD만 제공하고, Star를 리뷰·평점으로 표현하거나 검색 리치 결과를 약속하지 않는다. 일반 404 문서는 `noindex`이며 실제 잘못된 URL의 HTTP 404 응답은 배포 호스트에서 확인해야 한다.

검색 가능하도록 만든 것과 **실제 검색엔진에 색인된 것**은 다르다. 배포 후 운영자가 해야 할 확인:

1. 한국어·영어 URL이 UTF-8 HTML과 HTTP 200을 반환하고, 잘못된 URL은 404인지 확인한다.
2. Search Console에서 소유권을 확인한 URL-prefix 속성에 `https://currenjin.github.io/site-for-developers/`를 등록한다. 다른 사이트 속성이나 토큰을 추정해서 사용하지 않는다.
3. Search Console의 Sitemaps에 `https://currenjin.github.io/site-for-developers/sitemap.xml`을 제출한다. 레거시 sitemap ping 주소는 사용하지 않는다.
4. 두 언어 루트를 URL 검사하여 실시간 테스트·렌더링 HTML·선택된 canonical·색인 상태를 확인한다. 필요하면 색인 생성을 요청하고 이후 결과를 다시 확인한다. 사이트맵 제출이나 요청은 색인·순위를 보장하지 않는다.

`robots.txt`의 유효 위치는 호스트 루트다. 프로젝트 하위 `robots.txt`는 추가하지 않으며 다른 저장소의 루트 파일도 수정하지 않는다. sitemap은 실제 두 언어 루트만 담고, 일일 Star 갱신을 콘텐츠 변경처럼 보이게 하는 빌드 시각 `lastmod`는 넣지 않는다. 분류별 얇은 페이지나 존재하지 않는 리소스 상세 URL도 생성하지 않는다.

Google 공식 참고:
- JavaScript SEO: https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics
- Sitemap 작성·제출: https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
- Search Console 소유권: https://support.google.com/webmasters/answer/9008080

전체 회귀 검증은 반드시 최신 빌드 후 실행한다. `test_static_seo.py`는 실제 브라우저의 JavaScript 비활성 모드에서 두 언어의 전체 ID·URL·라벨·분류와 수를 검사하고, 초기 DOM 재사용·검색·초기화·로딩 실패·HTML/JSON-LD 삽입 안전성을 검증한다.

```sh
python3 scripts/build_site.py
python3 -m unittest discover -s tests -v
```

## 되돌리기

디자인 변경은 `web/`에서, 목록 변경은 README에서 수정한다. 문제가 생기면 해당 변경을 Git에서 되돌리고 `main`의 검증·배포가 끝난 뒤 실제 공개 파일을 확인한다. README와 기여 기록을 삭제하거나 별도의 목록으로 옮겨 복구하지 않는다.
