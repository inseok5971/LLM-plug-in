# ⚡ AI 플러그인 스위치보드 (Plugin Switchboard)

영어가 익숙하지 않은 사용자를 위해, 복잡한 AI 플러그인들을 **8대 목적별 카테고리**로 묶고 **직관적인 토글 스위치(ON/OFF)**로 제어하는 시스템입니다.

---

## 🎯 주요 기능

1. **8대 표준 한국어 카테고리**
   - 🎬 영상 만들기 및 편집 (Runway, Luma, Kling, Pika 등)
   - 🎨 그림 및 디자인 (Midjourney, FLUX, DALL-E 등)
   - 🎵 목소리 및 음악 (ElevenLabs 성우, Suno 작곡, Whisper 받아쓰기)
   - 🔍 인터넷 검색 및 최신 정보 (구글 실시간 검색, Perplexity)
   - 📄 문서·업무·이메일 (스마트 PDF 분석기, Notion, 구글 캘린더)
   - 💻 내 컴퓨터 파일 & 시스템 제어 (폴더 탐색기, 터미널 실행기)
   - 🌐 웹 브라우저 자동 조작 (Puppeteer 자동 클릭/수집)
   - 📊 통계 & 데이터 분석 (차트 시각화)

2. **💬 원클릭 전체 끄기 (순수 대화 모드)**
   - 평소에 일반 질문이나 번역만 할 때, 무거운 영상/이미지 플러그인이 발동되어 토큰이 낭비되거나 오류가 나는 것을 원천 차단합니다.

3. **자유로운 다중/개별 스위칭**
   - 원하는 플러그인을 1개만 켜도 되고, 여러 개를 동시에 켜서 비교할 수도 있습니다.
   - 각 카테고리별 **[모두 끄기]** 버튼으로 손쉬운 정리 가능.

4. **실시간 검색 & 새 플러그인 등록**
   - 상단 검색창에서 한글 이름이나 설명으로 즉시 검색.
   - 우측 상단 `[+ 플러그인 등록]` 버튼으로 새로운 도구를 바로 추가 가능.

---

## 🚀 실행 방법

### 방법 1. 웹 대시보드 바로 켜기 (간편 실행)
터미널에서 아래 명령어를 실행하거나, `start.sh` 파일을 더블 클릭하세요:

```bash
./start.sh
```
자동으로 브라우저가 열리며 `http://localhost:8765` 대시보드가 실행됩니다.

---

### 방법 2. Claude Desktop / Antigravity에 실제 연동하기 (MCP 연동)

Claude Desktop 설정 파일(`~/Library/Application Support/Claude/claude_desktop_config.json`)의 `mcpServers` 항목에 아래 내용을 추가합니다:

```json
{
  "mcpServers": {
    "plugin-switchboard": {
      "command": "python3",
      "args": [
        "/Users/jis/Desktop/Portfolio/플러그인/server.py",
        "--mcp"
      ]
    }
  }
}
```

이제 대시보드 웹 화면에서 스위치를 켜고 끄면, **Claude는 현재 [ON]으로 켜진 플러그인의 도구만 인식**하게 됩니다!
대화창에서 *"현재 활성 플러그인 알려줘"*라고 물어보면 스위치보드가 현재 켜진 도구 목록을 알려줍니다.

---

## 📁 파일 구조
- `index.html`: 미니멀하고 세련된 웹 대시보드 UI
- `plugins_data.json`: 8대 카테고리 및 플러그인 목록, 상태 저장소
- `server.py`: 웹 서버 및 MCP(Model Context Protocol) 중계 게이트웨이
- `start.sh`: 원클릭 실행 스크립트
