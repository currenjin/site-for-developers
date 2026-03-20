# How to Contribute

이 저장소는 **README.md 단일 소스**로 링크를 관리합니다.

---

## 기여 전 체크

추가/수정하려는 사이트가 아래 조건을 만족하는지 확인해주세요.

- 개발자에게 실질적으로 도움이 되는 사이트 또는 도구
- 정상 접속 가능한 사이트
- 기존 목록과 중복되지 않는 사이트
- 광고/스팸 목적이 아닌 사이트

---

## 기여 방법 (PR)

### 1) Fork
이 저장소를 Fork 합니다.

### 2) Clone
```bash
git clone https://github.com/[your-username]/site-for-developers.git
cd site-for-developers
```

### 3) 브랜치 생성
```bash
git checkout -b docs/update-links
```

### 4) README 수정
- 적절한 카테고리에 사이트를 추가/수정/삭제
- AI 도구는 `AI 🤖` 섹션의 해당 서브카테고리에 추가
- 기존 라벨 표기 방식(`<sub>KR</sub>`, `<sub>EN</sub>`, `<sub>F</sub>`, `<sub>$</sub>`, `<sub>O</sub>`)을 맞춰주세요.
- 링크/설명 문구 톤은 주변 항목과 일관되게 유지해주세요.

### 5) Commit
```bash
git add README.md
git commit -m "docs: add [사이트명]"
```

### 6) Push
```bash
git push origin docs/update-links
```

### 7) Pull Request 생성
원본 저장소(`currenjin/site-for-developers`)로 PR을 생성합니다.

---

## PR 리뷰 기준

- 링크가 실제로 열리는가?
- 중복 항목은 없는가?
- 카테고리가 적절한가?
- 라벨/설명 형식이 일관적인가?

---

## 이슈 제보

- 새로운 사이트 제안: `💬 아이디어 및 제안`
- 오류/오타/죽은 링크: `🐛 버그 신고`

감사합니다 🙌
