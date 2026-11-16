(function () {
  // 이미 주입되어 있으면 중복 실행 방지
  if (document.getElementById("llm-switchboard-trigger")) return;

  const CATEGORIES = [
    { id: "video", icon: "🎬", name: "영상 만들기 및 편집", desc: "고화질 동영상을 만드는 플러그인" },
    { id: "image", icon: "🎨", name: "그림 및 디자인 그리기", desc: "일러스트, 캐릭터, 로고를 그리는 플러그인" },
    { id: "audio", icon: "🎵", name: "목소리 및 음악", desc: "AI 성우 목소리, 노래 작곡, 음성 받아쓰기" },
    { id: "search", icon: "🔍", name: "인터넷 검색 및 최신 정보", desc: "실시간 뉴스, 주가, 웹 정보를 가져오는 플러그인" },
    { id: "office", icon: "📄", name: "문서·업무·이메일", desc: "PDF 요약, 노션 연동, 구글 캘린더 일정 등록" },
    { id: "system", icon: "💻", name: "내 컴퓨터 파일 & 시스템 제어", desc: "컴퓨터 폴더 파일 읽기/쓰기, 명령어 실행" },
    { id: "browser", icon: "🌐", name: "웹 브라우저 자동 조작", desc: "AI가 직접 브라우저를 열어 정보 수집" },
    { id: "data", icon: "📊", name: "통계 & 데이터 분석", desc: "엑셀 데이터를 분석하고 예쁜 차트 생성" }
  ];

  const PLUGINS = [
    { id: "runway", name: "런웨이 (Runway Gen-3)", cat: "video", tag: "실사 영화급", desc: "초고화질 실사 영화 수준 영상 생성" },
    { id: "luma", name: "루마 드림머신 (Luma)", cat: "video", tag: "카메라 무빙", desc: "부드러운 시점 회전과 앵글 이동" },
    { id: "kling", name: "클링 (Kling AI)", cat: "video", tag: "인물 동작", desc: "사람 표정과 걷기 등 자연스러운 신체 묘사" },
    { id: "pika", name: "피카 (Pika 2.0)", cat: "video", tag: "특수효과", desc: "물체가 녹거나 터지는 숏폼 효과" },

    { id: "midjourney", name: "미드저니 (Midjourney)", cat: "image", tag: "최고 퀄리티", desc: "가장 뛰어난 예술적 일러스트 그림" },
    { id: "flux", name: "플럭스 (FLUX.1)", cat: "image", tag: "글자 표기", desc: "그림 속 영어 텍스트를 정확하게 표현" },
    { id: "dalle", name: "달리 3 (DALL-E 3)", cat: "image", tag: "설명문 정확도", desc: "복잡한 설명문도 디테일하게 그림" },

    { id: "elevenlabs", name: "일레븐랩스 (ElevenLabs)", cat: "audio", tag: "AI 성우", desc: "자연스러운 목소리로 오디오 녹음" },
    { id: "suno", name: "수노 (Suno 작곡)", cat: "audio", tag: "노래 작곡", desc: "보컬 포함 완성형 노래 음악 작곡" },
    { id: "whisper", name: "위스퍼 (Whisper 받아쓰기)", cat: "audio", tag: "회의록", desc: "녹음 파일을 정확한 텍스트로 변환" },

    { id: "google-search", name: "구글 실시간 웹 검색", cat: "search", tag: "최신 뉴스", desc: "오늘의 뉴스, 실시간 주가 탐색" },
    { id: "perplexity", name: "퍼플렉시티 (Perplexity)", cat: "search", tag: "출처 요약", desc: "출처 링크와 함께 핵심 요약" },

    { id: "pdf-analyzer", name: "스마트 PDF 분석기", cat: "office", tag: "문서 요약", desc: "긴 계약서나 보고서 PDF의 핵심 요약" },
    { id: "notion", name: "노션 (Notion 연동)", cat: "office", tag: "메모 저장", desc: "대화 내용을 내 노션에 새 메모로 저장" },
    { id: "google-calendar", name: "구글 캘린더 일정 관리", cat: "office", tag: "일정 등록", desc: "약속 일정을 캘린더에 바로 등록" },

    { id: "filesystem", name: "컴퓨터 파일 탐색기", cat: "system", tag: "내 컴퓨터", desc: "내 컴퓨터 폴더 안의 파일 읽기/쓰기" },
    { id: "terminal", name: "터미널 명령어 실행기", cat: "system", tag: "명령어", desc: "컴퓨터 설정 및 프로그램 대신 실행" },

    { id: "puppeteer", name: "웹 브라우저 자동 조작기", cat: "browser", tag: "자동 클릭", desc: "브라우저 화면 캡처 및 데이터 수집" },

    { id: "chart-visualizer", name: "데이터 차트 시각화", cat: "data", tag: "예쁜 그래프", desc: "엑셀 표 데이터를 보기 쉬운 그래프로 변환" }
  ];

  let states = {};

  function loadStates(cb) {
    if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
      chrome.storage.local.get(["plugin_states"], (res) => {
        states = res.plugin_states || { "google-search": true };
        if (cb) cb();
      });
    } else {
      try {
        states = JSON.parse(localStorage.getItem("plugin_states")) || { "google-search": true };
      } catch (e) {
        states = { "google-search": true };
      }
      if (cb) cb();
    }
  }

  function saveStates() {
    if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
      chrome.storage.local.set({ "plugin_states": states });
    } else {
      localStorage.setItem("plugin_states", JSON.stringify(states));
    }
    updateBadge();
  }

  // 1. 우측 하단 플로팅 트리거 버튼 생성
  const trigger = document.createElement("button");
  trigger.id = "llm-switchboard-trigger";
  trigger.innerHTML = `
    <span>⚡ 스위치보드</span>
    <span class="trigger-badge" id="sb-trigger-count">1</span>
  `;
  document.body.appendChild(trigger);

  // 2. 우측 슬라이드 사이드바 패널 생성
  const sidebar = document.createElement("div");
  sidebar.id = "llm-switchboard-sidebar";
  sidebar.innerHTML = `
    <div class="sb-header">
      <div>
        <div class="sb-title">⚡ AI 플러그인 스위치보드</div>
        <div class="sb-sub">현재 화면에서 바로 켜고 끌 수 있습니다.</div>
      </div>
      <button class="sb-close" id="sb-close-btn">✕</button>
    </div>
    <div class="sb-body">
      <!-- 프리셋 바 -->
      <div style="background: #FFFFFF; padding: 12px; border-radius: 10px; border: 1px solid #E5E7EB; margin-bottom: 12px;">
        <div style="font-size: 11px; font-weight: 700; color: #6B7280; margin-bottom: 8px;">원클릭 빠른 모드</div>
        <div style="display: flex; flex-wrap: wrap; gap: 6px;">
          <button id="sb-p-none" style="font-size: 11px; padding: 5px 8px; border-radius: 6px; background: #FEE2E2; color: #DC2626; border: 1px solid #FECACA; cursor: pointer; font-weight: 700;">✕ 전체 끄기</button>
          <button id="sb-p-video" style="font-size: 11px; padding: 5px 8px; border-radius: 6px; background: #F3F4F6; border: 1px solid #E5E7EB; cursor: pointer;">🎬 영상 모드</button>
          <button id="sb-p-image" style="font-size: 11px; padding: 5px 8px; border-radius: 6px; background: #F3F4F6; border: 1px solid #E5E7EB; cursor: pointer;">🎨 그림 모드</button>
          <button id="sb-p-search" style="font-size: 11px; padding: 5px 8px; border-radius: 6px; background: #F3F4F6; border: 1px solid #E5E7EB; cursor: pointer;">🔍 검색 모드</button>
        </div>
      </div>

      <!-- 카테고리 목록 -->
      <div id="sb-cat-list" style="display: flex; flex-direction: column; gap: 10px;"></div>
    </div>
  `;
  document.body.appendChild(sidebar);

  // 이벤트 바인딩
  trigger.addEventListener("click", () => {
    sidebar.classList.toggle("open");
  });
  document.getElementById("sb-close-btn").addEventListener("click", () => {
    sidebar.classList.remove("open");
  });

  // 프리셋 바인딩
  document.getElementById("sb-p-none").addEventListener("click", () => {
    Object.keys(states).forEach(k => states[k] = false);
    saveStates();
    renderSidebar();
  });
  document.getElementById("sb-p-video").addEventListener("click", () => {
    Object.keys(states).forEach(k => states[k] = false);
    states["runway"] = true;
    saveStates();
    renderSidebar();
  });
  document.getElementById("sb-p-image").addEventListener("click", () => {
    Object.keys(states).forEach(k => states[k] = false);
    states["midjourney"] = true;
    saveStates();
    renderSidebar();
  });
  document.getElementById("sb-p-search").addEventListener("click", () => {
    Object.keys(states).forEach(k => states[k] = false);
    states["google-search"] = true;
    saveStates();
    renderSidebar();
  });

  function renderSidebar() {
    const root = document.getElementById("sb-cat-list");
    root.innerHTML = "";

    CATEGORIES.forEach(cat => {
      const catPlugins = PLUGINS.filter(p => p.cat === cat.id);
      const activeCount = catPlugins.filter(p => states[p.id]).length;

      const card = document.createElement("div");
      card.style.cssText = "background: #FFFFFF; border-radius: 10px; border: 1px solid #E5E7EB; overflow: hidden;";

      const details = document.createElement("details");
      details.open = true;

      details.innerHTML = `
        <summary style="padding: 10px 12px; cursor: pointer; display: flex; align-items: center; justify-content: space-between; user-select: none; background: #FFFFFF;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 16px;">${cat.icon}</span>
            <div>
              <div style="font-size: 12px; font-weight: 700; color: #111827; display: flex; align-items: center; gap: 6px;">
                <span>${cat.name}</span>
                <span style="font-size: 9px; font-weight: 600; padding: 1px 5px; border-radius: 4px; ${activeCount > 0 ? 'background: #EFF6FF; color: #2563EB; border: 1px solid #DBEAFE;' : 'background: #F3F4F6; color: #6B7280;'}">
                  ${activeCount} / ${catPlugins.length} 켜짐
                </span>
              </div>
            </div>
          </div>
          <button class="sb-cat-off-btn" style="font-size: 10px; color: #6B7280; background: #FFF; border: 1px solid #D1D5DB; padding: 2px 6px; border-radius: 4px; cursor: pointer;">모두 끄기</button>
        </summary>
        <div style="background: #F9FAFB; border-top: 1px solid #F3F4F6; padding: 8px 10px; display: flex; flex-direction: column; gap: 6px;">
          ${catPlugins.map(p => `
            <div style="background: #FFF; border: 1px solid #E5E7EB; border-radius: 6px; padding: 8px 10px; display: flex; align-items: center; justify-content: space-between;">
              <div style="padding-right: 6px;">
                <div style="display: flex; align-items: center; gap: 4px;">
                  <span style="font-size: 11px; font-weight: 700; color: #111827;">${p.name}</span>
                  <span style="font-size: 9px; color: #6B7280; background: #F3F4F6; padding: 0 4px; border-radius: 3px;">${p.tag}</span>
                </div>
                <div style="font-size: 10px; color: #6B7280; margin-top: 2px;">${p.desc}</div>
              </div>
              <input type="checkbox" data-p-id="${p.id}" ${states[p.id] ? "checked" : ""} style="cursor: pointer; width: 16px; height: 16px;">
            </div>
          `).join("")}
        </div>
      `;

      // 모두 끄기
      details.querySelector(".sb-cat-off-btn").addEventListener("click", (e) => {
        e.stopPropagation();
        e.preventDefault();
        catPlugins.forEach(p => states[p.id] = false);
        saveStates();
        renderSidebar();
      });

      // 개별 스위치
      details.querySelectorAll(`input[type="checkbox"]`).forEach(chk => {
        chk.addEventListener("change", (e) => {
          const id = e.target.getAttribute("data-p-id");
          states[id] = e.target.checked;
          saveStates();
          renderSidebar();
        });
      });

      card.appendChild(details);
      root.appendChild(card);
    });

    updateBadge();
  }

  function updateBadge() {
    const count = Object.values(states).filter(Boolean).length;
    const badge = document.getElementById("sb-trigger-count");
    if (badge) badge.textContent = count;
  }

  // 팝업에서 보낸 메시지 수신
  if (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.onMessage) {
    chrome.runtime.onMessage.addListener((msg) => {
      if (msg.type === "STATE_UPDATED") {
        states = msg.states;
        renderSidebar();
      }
    });
  }

  loadStates(() => {
    renderSidebar();
  });
})();
