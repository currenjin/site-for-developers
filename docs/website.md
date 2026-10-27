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

## 되돌리기

디자인 변경은 `web/`에서, 목록 변경은 README에서 수정한다. 문제가 생기면 해당 변경을 Git에서 되돌리고 `main`의 검증·배포가 끝난 뒤 실제 공개 파일을 확인한다. README와 기여 기록을 삭제하거나 별도의 목록으로 옮겨 복구하지 않는다.
