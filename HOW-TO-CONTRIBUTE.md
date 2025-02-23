# 목차

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
  - [2. Clone forked repository](#2-clone-forked-repository-2)
  - [3. Open Android Studio](#3-open-android-studio)
  - [4. Start android](#4-start-android)
  - [5. Commit your changes](#5-commit-your-changes-1)
  - [6. Push yout commit](#6-push-yout-commit-1)
  - [7. Register pull requerst for your commit](#7-register-pull-requerst-for-your-commit-1)
  - [8. Pull request has been approved](#8-pull-request-has-been-approved-1)

## How to contribute

아래의 방법으로 Pull Request를 올려주시면 됩니다.<br/>
Site For Developers는 GitHub README.md, 웹사이트, 안드로이드 앱으로 구성되어 있습니다.<br/>
지금 기여하셔서 Site For Developers를 더 유익하고 편리한 레포지토리로 만들어 주세요!

## 시작하기에 앞서

- 이 Repository의 정식 명칭은 **Site For Developers** 입니다.

### 1. 데이터 작성 규칙

- 데이터 작성은 아래의 작성 형식을 따르면 됩니다.
  - **title 태그**는 웹사이트 head의 <title>을 작성하시면 됩니다.
  - **content 태그**는 웹사이트 head의 <meta name="description">을 작성하시면 됩니다. (description이 존재하지 않는다면 title로 대체하여 주시기 바랍니다.)
  - **feature 태그**는 웹사이트의 특징에 따라
  - **img_url 태그**는 웹사이트 head의 <link rel="icon">을 작성하시면 됩니다. (icon이 존재하지 않는다면 shortcut icon을 작성하시고 둘 다 없다면 공백으로 두시면 됩니다.)
  - **link 태그**는 웹사이트의 주소를 작성하시면 됩니다.

```
{
"title": "",
"content": "",
"feature": [""],
"img_url": "",
"link": ""
}
```

## README.md

### 1. Fork this repository

이 레포지토리를 포크해 주세요. [포크하는법](https://ittrue.tistory.com/90)

### 2. Clone forked repository

포크한 레포지토리를 clone해 주세요.

```
$ git clone https://github.com/[username]/site-for-developers.git
$ cd site-for-developers
```

### 3. Commit your changes

변경사항을 만들고 커밋해주세요.

```
$ git add .
$ git commit -m "[your description]"
```

### 4. Push your commit

커밋을 포크한 레포지토리로 push해 주세요.

⚠ 이 명령어에서 'origin'은 당신이 포크한 레포지토리여야 합니다.

```
$ git push origin main
```

### 5. Register pull request for your commit

Pull Request를 등록해 주세요. [Pull Request 등록하는법](https://wayhome25.github.io/git/2017/07/08/git-first-pull-request-story/)

### 6. Pull request has been approved

🎉 관리자에 의해 Pull Request가 승인되면 당신은 기여자 명단에 올라가게 됩니다 🎉

## Website

### 1. Fork this repository

이 레포지토리를 포크해 주세요. [포크하는법](https://ittrue.tistory.com/90)

> 포크하는 과정에서 "Copy the main branch only"의 체크박스를 해제해주세요.

### 2. Clone forked repository

포크한 레포지토리를 clone해 주세요.

```
$ git clone -b website https://github.com/[username]/site-for-developers.git
$ cd site-for-developers
```

### 3. Install depencies

필요한 의존성들을 설치해주세요.

```
$ pnpm install
```

### 4. Start website

해당 웹사이트를 실행해보세요.

```
$ pnpm start
```

### 5. Commit your changes

현재까지 아무런 문제가 없다면 변경사항을 만들고 커밋해주세요.

```
$ git add .
$ git commit -m "[your description]"
```

### 6. Push your commit

커밋을 포크한 레포지토리로 push해 주세요.

⚠ 이 명령어에서 'origin'은 당신이 포크한 레포지토리의 리모트여야 합니다.

```
$ git push origin website
```

### 7. Register pull request for your commit

Pull Request를 등록해 주세요. [Pull Request 등록하는법](https://wayhome25.github.io/git/2017/07/08/git-first-pull-request-story/)

### 8. Pull request has been approved

🎉 관리자에 의해 Pull Request가 승인되면 당신은 기여자 명단에 올라가게 됩니다 🎉

## Android

### 1. Fork this repository

이 레포지토리를 포크해 주세요. [포크하는법](https://ittrue.tistory.com/90)

> 포크하는 과정에서 "Copy the main branch only"의 체크박스를 해제해주세요.

### 2. Clone forked repository

포크한 레포지토리를 clone해 주세요.

```
$ git clone -b website https://github.com/[username]/site-for-developers.git
$ cd site-for-developers
```

### 3. Open Android Studio

Android Studio를 실행해 주세요. [Android Studio 설치하는법](https://ineedtoprogramandweb.tistory.com/entry/AndroidStudio-%EC%95%88%EB%93%9C%EB%A1%9C%EC%9D%B4%EB%93%9C-%EC%8A%A4%ED%8A%9C%EB%94%94%EC%98%A4-%EC%84%A4%EC%B9%98%ED%95%98%EA%B8%B0-%EC%B5%9C%EC%8B%A0),
[Android Studio 실행하는법](https://bbmsk2.tistory.com/25)

### 4. Start android

Android app을 실행해보세요. [Android app 실행하는법](https://ju-hy.tistory.com/21)

### 5. Commit your changes

현재까지 아무런 문제가 없다면 변경사항을 만들고 커밋해주세요.

```
$ git add .
$ git commit -m "[your description]"
```

### 6. Push yout commit

커밋을 포크한 레포지토리로 push해 주세요.

⚠ 이 명령어에서 'origin'은 당신이 포크한 레포지토리의 리모트여야 합니다.

```
$ git push origin android
```

### 7. Register pull requerst for your commit

Pull Request를 등록해 주세요. [Pull Request 등록하는법](https://wayhome25.github.io/git/2017/07/08/git-first-pull-request-story/)

### 8. Pull request has been approved

🎉 관리자에 의해 Pull Request가 승인되면 당신은 기여자 명단에 올라가게 됩니다 🎉
