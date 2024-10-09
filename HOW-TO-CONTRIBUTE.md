# How to contribute

아래의 방법으로 Pull Request 를 올려주시면 됩니다.<br/>
Site For Developers는 GitHub README.md, 웹사이트, 안드로이드 앱이 있습니다.<br/>
지금 기여하셔서 Site For Developers를 더 유익하고 편리한 레포지토리로 만들어 주세요!

## 시작하기에 앞서

- 이 Repository의 정식 명칭은 **Site For Developers** 입니다.

### 1. 데이터 작성 규칙

- 신규 데이터 생성은 아래의 작성 형식을 따라야 합니다.
  - **title 태그**는 웹사이트 head에 명시되어 있는 title을 따라야 합니다.
  - **content 태그**는 웹사이트 head에 명시되어 있는 description을 따라야 합니다. (description이 존재하지 않는다면 title로 대체해주시기 바랍니다.)
  - **feature 태그**는 웹사이트에 특성에 맞게 아래 목록에서 선택하여 작성하셔야 합니다. <br/>
    (opensource: 오픈소스 / korean: 한국어 / english: 영어 /)

```
{
"title": "",
"content": "",
"feature": [""],
"category": "",
"img_url": "",
"link": ""
}
```

### 2. 브랜딩 규칙

## 목차

- [How to contrubute](#how-to-contribute)
- [시작하기에 앞서](#시작하기에-앞서)
  - [1. 데이터 작성 규칙](#1-데이터-작성-규칙)
  - [2. 브랜딩 규칙](#2-브랜딩-규칙)
- [목차](#목차)
- [README.md](#readmemd)
  - [1. Fork this repository](#1-fork-this-repository)
  - [2. Clone forked repository](#2-clone-forked-repository)
  - [3. Commit your changes](#3-commit-your-changes)
  - [4. Push your commit](#4-push-your-commit)
  - [5. Register pull request for your commit](#5-register-pull-request-for-your-commit)
  - [6. Pull request has been approved](#6-pull-request-has-been-approved)
- [Website](#website)
  - [1. Fork this repository](#1-fork-this-repository-1)
  - [2. Clone forked repository](#2-clone-forked-repository-1)
  - [3. Install depencies](#3-install-depencies)
  - [4. Start website](#4-start-website)
  - [5. Commit your changes](#5-commit-your-changes)
  - [6. Push your commit](#6-push-your-commit)
  - [7. Register pull request for your commit](#7-register-pull-request-for-your-commit)
  - [8. Pull request has been approved](#8-pull-request-has-been-approved)
- [Android](#android)
  - [1. Fork this repository](#1-fork-this-repository-2)
  - [2. Open Android Studio](#2-open-android-studio)
  - [3. Start android](#3-start-android)
  - [4. Commit your changes](#4-commit-your-changes)
  - [5. Push yout commit](#5-push-yout-commit)
  - [6. Register pull requerst for your commit](#6-register-pull-requerst-for-your-commit)
  - [7. Pull request has been approved](#7-pull-request-has-been-approved)

## README.md

### 1. Fork this repository

이 Repository를 Fork해 주세요. [Fork 하는법](https://ittrue.tistory.com/90)

### 2. Clone forked repository

Fork된 Repository 를 Clone해 주세요.

```
$ git clone -b main https://github.com/[your name]/site-for-developers
$ cd site-for-developers
```

### 3. Commit your changes

변경사항을 만들고 커밋해주세요.

**⚠ 목록을 추가, 변경할때는 설명과 이미지를 작성하지 않으셔도 됩니다.**

```
$ git add .
$ git commit -m "[your description]"
```

### 4. Push your commit

커밋을 Fork된 Repository로 Push해 주세요.

⚠ 이 명령어에서 'origin'은 당신이 포크한 레포지토리여야 합니다.

```
$ git push origin main
```

### 5. Register pull request for your commit

Pull Request를 등록해 주세요. [Pull Request 등록하는법](https://wayhome25.github.io/git/2017/07/08/git-first-pull-request-story/)

### 6. Pull request has been approved

🎉 관리자에 의하여 당신의 Pull Request가 승인되면 당신은 기여자 명단에 올라가게 됩니다 🎉

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
$ npm start
```

### 5. Commit your changes

현재까지 아무런 문제가 없다면 변경사항을 만들고 커밋해주세요.

```
$ git add .
$ git commit -m "[your description]"
```

### 6. Push your commit

커밋을 포크한 레포지토리로 Push해 주세요.

⚠ 이 명령어에서 'origin'은 당신이 포크한 레포지토리의 리모트여야 합니다.

```
$ git push origin website
```

### 7. Register pull request for your commit

Pull Request를 등록해 주세요. [Pull Request 등록하는법](https://wayhome25.github.io/git/2017/07/08/git-first-pull-request-story/)

### 8. Pull request has been approved

🎉 관리자에 의하여 당신의 Pull Request가 승인되면 당신은 기여자 명단에 올라가게 됩니다 🎉

## Android

### 1. Fork this repository

이 Repository를 Fork해 주세요. [Fork 하는법](https://ittrue.tistory.com/90)

⚠ 주의: Fork 과정에서 "Copy the main branch only"의 체크박스을 해제해주세요.

### 2. Open Android Studio

Android Studio를 실행해 주세요. [Android Studio 설치하는법](https://ineedtoprogramandweb.tistory.com/entry/AndroidStudio-%EC%95%88%EB%93%9C%EB%A1%9C%EC%9D%B4%EB%93%9C-%EC%8A%A4%ED%8A%9C%EB%94%94%EC%98%A4-%EC%84%A4%EC%B9%98%ED%95%98%EA%B8%B0-%EC%B5%9C%EC%8B%A0),
[Android Studio 실행하는법](https://bbmsk2.tistory.com/25)

### 3. Start android

해당 Android app을 실행해보세요. [Android app 실행하는법](https://ju-hy.tistory.com/21)

### 4. Commit your changes

현재까지 아무런 문제가 없다면 변경사항을 만들고 커밋해주세요.

```
$ git add .
$ git commit -m "[your description]"
```

### 5. Push yout commit

커밋을 포크한 레포지토리로 Push해 주세요.

⚠ 이 명령어에서 'origin'은 당신이 포크한 레포지토리의 리모트여야 합니다.

```
$ git push origin android
```

### 6. Register pull requerst for your commit

Pull Request를 등록해 주세요. [Pull Request 등록하는법](https://wayhome25.github.io/git/2017/07/08/git-first-pull-request-story/)

### 7. Pull request has been approved

🎉 관리자에 의하여 당신의 Pull Request가 승인되면 당신은 기여자 명단에 올라가게 됩니다 🎉
