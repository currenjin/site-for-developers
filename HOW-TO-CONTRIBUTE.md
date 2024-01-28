# How to contribute
아래의 방법으로 Pull Request 를 올려주시면 됩니다.<br/>
Site For Developers는 GitHub README.md, 웹사이트, 안드로이드 앱이 있습니다.<br/>
지금 기여하셔서 Site For Developers를 더 유익하고 편리한 레포지토리로 만들어 주세요!

## README.md

### 1. Fork this respository
이 Repository를 Fork해 주세요. [Fork 하는법](https://ittrue.tistory.com/90)

### 2. Clone forked repository
Fork된 Repository 를 Clone해 주세요.

```
$ git clone -b main https://github.com/[your name]/site-for-developers
$ cd site-for-developers
```

### 3. Commit your changes
변경사항을 만들고 커밋해주세요.

```
$ git add .
$ git commit -m "[your description]"
$ git push origin main
```

### 4. Push your commit
커밋을 Fork된 Repository로 Push해 주세요.

```
$ git push origin main
```

### 5. Register pull request for your commit
Pull Request를 등록해 주세요. [Pull Request 등록하는법](https://wayhome25.github.io/git/2017/07/08/git-first-pull-request-story/)

## Website

### 1. Fork this repository
이 Repository를 Fork해 주세요. [Fork 하는법](https://ittrue.tistory.com/90)

⚠ 주의: Fork 과정에서 "Copy the main branch only"의 체크박스을 해제해주세요.

### 2. Clone forked repository
Fork된 Repository를 Clone해 주세요.

```
$ git clone -b website https://github.com/[your name]/site-for-developers
$ cd site-for-developers
```

### 3. Install depencies
필요한 의존성들을 설치해주세요.

```
$ npm install
```

### 4. Start website
해당 웹사이트를 실행해보세요.

```
$ npm run start
```

### 5. Commit your changes
현재까지 아무런 문제가 없다면 변경사항을 만들고 커밋해주세요.

```
$ git add .
$ git commit -m "[your description]"
$ git push origin main
```

### 6. Push your commit
커밋을 Fork된 Repository로 Push해 주세요.

```
$ git push origin website
```

### 7. Register pull request for your commit
Pull Request를 등록해 주세요. [Pull Request 등록하는법](https://wayhome25.github.io/git/2017/07/08/git-first-pull-request-story/)