# 초시공요새 마크로스 (PS2) 한글패치

PS2 일본판 **超時空要塞マクロス (SLPM-65405)** 용 비공식 한국어 패치입니다. 브리핑·튜토리얼·스토리 서문·메뉴·시스템 메시지와 글자 그림을 한국어로 바꾸고, 원래 글자가 나오지 않던 **미션 중 무선 음성에 한국어 자막**이 나오게 했습니다. 현재 배포판은 **v1.0.1 (2026-10-07)** 입니다.

[패치 다운로드](https://github.com/snake759494/macross-ps2-korean-patch/releases/latest) · [기술 설명](docs/TECHNICAL.md) · [재빌드](docs/BUILD.md) · [변경 기록](CHANGELOG.md) · [권리 안내](RIGHTS.md)

릴리즈 첨부 파일은 **Macross_PS2_KO_v1.0.1.xdelta 하나**입니다. 저장소에는 제작 소스·번역·검증 자료만 공개합니다. 원본 및 완성 디스크 이미지, 추출한 게임 파일, 글꼴 파일, 외부 실행 파일, 일본어 원문은 포함하지 않습니다. GitHub 가 자동 생성하는 Source code ZIP/TAR 는 저장소 소스의 압축본이며 게임 파일이 아닙니다.

> ⚠️ `translation/strings_ko.json` 에는 게임 대사 번역 전문이 들어 있어 **줄거리 스포일러**가 포함됩니다.

## 대상 버전

이 패치는 **PS2 일본판 SLPM-65405 의 DVD ISO (2,048 바이트 섹터)** 에만 적용합니다. 파일 이름보다 아래 크기와 해시가 일치하는지가 중요합니다.

| 항목 | 값 |
| --- | --- |
| 게임 ID | SLPM-65405 |
| 원본 형식 | 수정되지 않은 일본판 DVD ISO |
| 원본 ISO 크기 | 1,230,897,152 바이트 |
| **원본 ISO MD5** | `026bd41c9f3b0d55346ad634251eed51` |
| 원본 ISO SHA-256 | `221e4137cc1b197b262c58604143d92d2fdb3dd82d6b464870c6bbf1c68a27df` |
| xdelta 파일 크기 | 5,243,219 바이트 |
| xdelta SHA-256 | `ce0efc7e59744a90f74e5aa86813a653b29dc1aa2e21a8f8b17aa3cd15231c20` |
| 적용 결과 ISO 크기 | 1,230,897,152 바이트 (원본과 같음) |
| 적용 결과 ISO SHA-256 | `a82892947eb4a7d8d1ade30ecc4b06262940459da6f4e1517676f0df0fa1a4db` |

## 패치 적용 방법

### Windows 에서 원본 확인

```powershell
Get-FileHash -Algorithm MD5 -LiteralPath '.\Chou Jikuu Yousai Macross (Japan).iso'
```

위 표와 다르면 적용을 중단하세요. CHD·CSO 등으로 변환한 이미지에는 적용할 수 없습니다.

### xdelta UI 사용

1. 릴리즈에서 `Macross_PS2_KO_v1.0.1.xdelta` 를 받습니다.
2. xdelta3 패치를 지원하는 도구의 **Apply Patch** 기능을 엽니다.
3. **Patch** 에 xdelta 파일, **Source File** 에 해시가 일치하는 원본 `.iso` 를 선택합니다.
4. **Output File** 에 새 파일명(예: `Chou Jikuu Yousai Macross (Japan) (Korean).iso`)을 지정합니다.

xdelta 는 호환성을 위해 2차 압축과 파일 경로 헤더 없이 만들었습니다(`-e -9 -S none -A`).

### 명령줄 사용

```powershell
.\xdelta3.exe -d -s '.\Chou Jikuu Yousai Macross (Japan).iso' '.\Macross_PS2_KO_v1.0.1.xdelta' '.\Chou Jikuu Yousai Macross (Japan) (Korean).iso'
```

## 한글화 범위

- 게임 문장 2,970개: 브리핑, 튜토리얼, 스토리 서문, 미션 무선 대사, 메뉴, 미션 목표 (영문·숫자만 있는 111개는 원문 유지)
- **미션 중 음성 자막**: 대사 데이터의 표시 속성을 켜서 게임 내장 대사창(얼굴창 옆)에 자막 표시
- 실행파일 시스템 메시지 102개 (메모리 카드, HDD, 조이스틱 보정)
- 한글 글꼴 2,350자
- 글자 그림: 조작 설명, 스토리 줄거리, 에피소드 제목·목록, 기체 설명, 메뉴 제목, 옵션 하단 안내, 메모리 카드 화면, 저장 확인창, 스테이지 제목 21장
- 그대로 둔 것: 타이틀 로고, 저작권 표기, 영어로 된 그림, 엠블럼 한자 그림
- 동영상 4편(오프닝·홍보·엔딩 2종): 대사 음성과 화면 속 일본어가 없어 자막을 넣지 않았습니다

## 알려진 점

- PCSX2 에서 부팅, 타이틀, 메인 메뉴, 스토리 서문, 튜토리얼 대화·미션(무선 자막), 메모리 카드 선택·저장 화면을 확인했습니다. 전체 스토리 완주와 실기 확인은 하지 않았습니다.
- 대사창 글자가 잘리거나 일본어가 남은 화면을 발견하면 이슈로 스크린샷과 함께 알려 주세요.
