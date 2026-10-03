# 재빌드

필요: Python 3.13, numpy, Pillow, capstone, pycdlib, fontTools, NanumSquare Neo 글꼴(작업 폴더에 `NanumSquareNeo-*.ttf`), xdelta3.

1. 작업 폴더에 원본 `Chou Jikuu Yousai Macross (Japan).iso` 와 이 저장소의 `tools/`, `translation/` 을 둡니다.
2. 추출: `python tools/cvm.py -x` (CVM 내부 파일 → `work/ext/`), 실행파일·CMP 해제(`work/SLPM_654.05`, `work/dec/`)는 `tools/build.py` 가 사용하는 경로에 맞춰 `tools/cricmp.py` 로 풉니다.
3. 빌드: `python -X utf8 tools/build.py` → `Chou Jikuu Yousai Macross (Japan) (Korean).iso`
4. 패치: `xdelta3 -e -9 -S none -A -s 원본.iso 한글판.iso Macross_PS2_KO_v1.0.xdelta`

번역 수정은 `translation/strings_ko.json`(표번호_항목번호 → 문장), `translation/elf_ko.json`(실행파일 오프셋·용량), `translation/tex/*.json`(글자 그림 상자·문구)만 고치면 됩니다.
