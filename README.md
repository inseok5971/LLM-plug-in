# ⚡ AI 플러그인 스위치보드 (Unified AI Switchboard)

> **Claude, Antigravity, Cursor, Gemini, GPT 전용 통합 플러그인 스위치 리모컨**  
> 윈도우(Windows) & 맥(macOS) 100% 공용 지원 (데스크톱 미니 위젯)

<p align="center">
  <img src="https://img.shields.io/badge/Standard-MCP%20(Model%20Context%20Protocol)-blue?style=flat-square" alt="MCP" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-success?style=flat-square" alt="Platforms" />
  <img src="https://img.shields.io/badge/All--in--One-Claude%20%7C%20Antigravity%20%7C%20Cursor%20%7C%20Gemini-orange?style=flat-square" alt="All AI" />
  <img src="https://img.shields.io/badge/Language-Korean%20(한국어)-purple?style=flat-square" alt="Korean Support" />
</p>

---

## 🧐 왜 만들었나요?

AI 파워 유저들은 웹 브라우저가 아니라 **Claude Desktop, Antigravity, Cursor** 같은 데스크톱 전용 앱을 주로 사용합니다.  
하지만 여러 플러그인을 깔아두면:
1. **도구 중복 호출 & 충돌**: 영상 하나 만드는데 여러 영상 모델이 한꺼번에 발동되거나 엉뚱한 도구가 실행됨.
2. **토큰 낭비 & 버그**: 가벼운 일상 질문이나 번역만 물어봤는데도 무거운 플러그인이 실행되어 비용과 시간이 낭비됨.

👉 **"내 모니터 구석에 작은 미니 리모컨 위젯을 띄워두고, 클릭 한 번으로 모든 AI 앱의 플러그인을 실시간으로 켜고 끌 수 있게 만들었습니다!"**

---

## 🖥️ 실제 동작 화면 (스마트폰 크기의 독립 위젯)

Claude나 Cursor 창 옆에 찰떡같이 띄워두고 스위치를 조작하세요:

```text
┌───────────────────────────────────────┐  ┌────────────────────────────────────┐
│ 💬 Claude / Antigravity / Cursor 앱   │  │ ⚡ AI 플러그인 스위치보드  [1개 켜짐]│
│                                       │  ├────────────────────────────────────┤
│                                       │  │ [✕ 전체 끄기] [🎬 영상] [🎨 그림]   │
│ [사용자]: 멋진 드론 영상 하나 만들어줘    │  ├────────────────────────────────────┤
│                                       │  │ ▼ 🎬 영상 만들기 및 편집 (1/4 켜짐) │
│ [Claude]: 활성화된 런웨이(Runway) 도구로 │  │   • 런웨이 (Runway Gen-3) [ ON ]│
│           영상을 생성을 시작합니다.     │  │   • 루마 (Luma)           [ OFF]│
│                                       │  │   • 클링 (Kling AI)       [ OFF]│
│                                       │  ├────────────────────────────────────┤
│                                       │  │ ▶ 🎨 그림 및 디자인 그리기 (0/3)   │
│                                       │  │ ▶ 🎵 목소리 및 음악 (0/3)          │
│                                       │  │ ▶ 🔍 인터넷 검색 및 최신 정보 (1/2) │
└───────────────────────────────────────┘  └────────────────────────────────────┘
```

---

## 🚀 10초 초간단 실행 방법 (윈도우 & 맥 동일)

1. 우측 상단 초록색 **[Code]** 버튼 -> **[Download ZIP]**을 눌러 다운로드 후 압축을 풉니다.
2. 내 컴퓨터에 맞는 실행 파일을 **더블 클릭**합니다:
   - **맥(Mac) 사용자**: `start_mac.command` 더블 클릭
   - **윈도우(Windows) 사용자**: `start_windows.bat` 더블 클릭
3. 화면에 예쁜 **미니 스위치보드 위젯 창**이 뜹니다!
4. 위젯 창 맨 아래의 **`[앱 자동 연동]`** 버튼을 한 번만 클릭하면, 내 컴퓨터의 Claude Desktop / Cursor 등에 **자동으로 스위치보드가 등록**됩니다. 🎉

---

## 💡 어떻게 모든 AI(Claude, 안티그래비티, Cursor 등)에 다 먹히나요?

지금 전 세계 AI 앱들이 도구를 연결하는 표준 규격인 **MCP(Model Context Protocol)**를 기반으로 작동합니다:

1. 사용자가 위젯에서 **런웨이(Runway)만 [ON]**으로 켭니다.
2. Claude, 안티그래비티, Cursor 등 어떤 AI 앱에 말을 걸어도,
3. 스위치보드가 **꺼져 있는 도구는 아예 숨겨버리고 켜진 도구만 AI에게 전달**합니다.
4. 따라서 모든 AI 앱이 일제히 스위치 상태에 맞춰 완벽하게 통제됩니다!

---

## 📂 8대 표준 카테고리 구성

- 🎬 **영상 만들기 및 편집**: 런웨이(Runway), 루마(Luma), 클링(Kling), 피카(Pika)
- 🎨 **그림 및 디자인 그리기**: 미드저니(Midjourney), 플럭스(FLUX), 달리 3(DALL-E 3)
- 🎵 **목소리 및 음악**: 일레븐랩스(ElevenLabs 성우), 수노(Suno 작곡), 위스퍼(Whisper 받아쓰기)
- 🔍 **인터넷 검색 및 최신 정보**: 구글 실시간 웹 검색, 퍼플렉시티(Perplexity)
- 📄 **문서·업무·이메일**: 스마트 PDF 분석기, 노션(Notion 연동), 구글 캘린더
- 💻 **내 컴퓨터 파일 & 시스템 제어**: 컴퓨터 폴더 파일 탐색기, 터미널 명령어 실행기
- 🌐 **웹 브라우저 자동 조작**: 웹 브라우저 자동 클릭 및 데이터 수집
- 📊 **통계 & 데이터 분석**: 데이터 차트 시각화 도구

---

## 🛠️ 수동 연동 가이드 (직접 설정 파일을 열고 싶을 때)

만약 수동으로 설정하고 싶다면, 각 AI 앱의 설정 파일(`claude_desktop_config.json` 등)의 `mcpServers`에 아래 내용을 넣어주시면 됩니다:

```json
{
  "mcpServers": {
    "plugin-switchboard": {
      "command": "python3",
      "args": [
        "이_폴더의_전체경로/main.py",
        "--mcp"
      ]
    }
  }
}
```

---

## 📄 라이선스
MIT License. 누구나 자유롭게 수정 및 배포하실 수 있습니다.
