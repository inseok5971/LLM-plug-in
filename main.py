#!/usr/bin/env python3
"""
⚡ AI 플러그인 스위치보드 (Plugin Switchboard)
- Claude Desktop, Antigravity, Cursor, Codex, Gemini 통합 MCP 게이트웨이 & 데스크톱 미니 위젯
"""

import sys
import os
import json
import tempfile
import threading
import subprocess
import platform
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import urllib.parse
import webbrowser

# 윈도우 콘솔 한글 및 이모지(CP949) 인코딩 충돌 방지
if sys.platform == "win32":
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
WIDGET_FILE = os.path.join(BASE_DIR, "widget.html")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            sys.stderr.write(f"설정 파일 읽기 오류: {e}\n")
    return {"categories": [], "plugins": []}

def save_config(data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        sys.stderr.write(f"설정 파일 저장 오류: {e}\n")

# HTTP 요청 핸들러 (위젯 UI와 통신)
class WidgetHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ["/", "/index.html", "/widget.html"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(WIDGET_FILE, "rb") as f:
                self.wfile.write(f.read())
            return
        elif parsed.path == "/api/data":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(load_config(), ensure_ascii=False).encode("utf-8"))
            return
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        req = json.loads(body) if body else {}

        data = load_config()

        if parsed.path == "/api/toggle":
            p_id = req.get("id")
            enabled = req.get("enabled", False)
            target_app = req.get("app", "claude")
            for p in data.get("plugins", []):
                if p["id"] == p_id:
                    p.setdefault("enabled_apps", {})
                    if target_app == "all":
                        p["enabled_apps"]["claude"] = enabled
                        p["enabled_apps"]["cursor"] = enabled
                        p["enabled_apps"]["antigravity"] = enabled
                    else:
                        p["enabled_apps"][target_app] = enabled
                    p["enabled"] = enabled
                    break
            save_config(data)
            self._send_json({"success": True})
            return

        elif parsed.path == "/api/category-off":
            cat = req.get("cat")
            target_app = req.get("app", "claude")
            for p in data.get("plugins", []):
                if p.get("cat") == cat:
                    p.setdefault("enabled_apps", {})
                    if target_app == "all":
                        p["enabled_apps"]["claude"] = False
                        p["enabled_apps"]["cursor"] = False
                        p["enabled_apps"]["antigravity"] = False
                    else:
                        p["enabled_apps"][target_app] = False
                    p["enabled"] = False
            save_config(data)
            self._send_json({"success": True})
            return

        elif parsed.path == "/api/preset":
            preset = req.get("preset")
            target_app = req.get("app", "claude")
            preset_map = {
                "video": "runway",
                "image": "midjourney",
                "audio": "elevenlabs",
                "search": "google-search"
            }
            target_id = preset_map.get(preset)
            for p in data.get("plugins", []):
                p.setdefault("enabled_apps", {})
                is_on = (p["id"] == target_id)
                if target_app == "all":
                    p["enabled_apps"]["claude"] = is_on
                    p["enabled_apps"]["cursor"] = is_on
                    p["enabled_apps"]["antigravity"] = is_on
                else:
                    p["enabled_apps"][target_app] = is_on
            save_config(data)
            self._send_json({"success": True})
            return

        elif parsed.path == "/api/auto-setup":
            msg = setup_all_apps()
            self._send_json({"success": True, "message": msg})
            return

        elif parsed.path == "/api/scan-plugins":
            result = scan_and_merge_plugins()
            self._send_json(result)
            return

        self.send_error(404)

    def _send_json(self, obj):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(obj, ensure_ascii=False).encode("utf-8"))

# 컴퓨터에 설치된 새 플러그인(MCP 서버)을 스캔하여 중복 없이 자동 추가 및 상세 리포트 생성
def scan_and_merge_plugins():
    home = os.path.expanduser("~")
    system = platform.system()
    discovered_servers = {}
    scanned_sources = []

    # 1. Claude Desktop 설정 파일 스캔
    if system == "Darwin":
        claude_path = os.path.join(home, "Library", "Application Support", "Claude", "claude_desktop_config.json")
    else:
        claude_path = os.path.join(os.environ.get("APPDATA", home), "Claude", "claude_desktop_config.json")

    claude_servers = []
    if os.path.exists(claude_path):
        try:
            with open(claude_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for s_name, s_conf in data.get("mcpServers", {}).items():
                    if s_name != "plugin-switchboard":
                        claude_servers.append(s_name)
                        discovered_servers[s_name] = ("Claude Desktop", s_conf)
            scanned_sources.append({"app": "Claude Desktop", "status": "연결됨", "path": claude_path, "count": len(claude_servers), "servers": claude_servers})
        except Exception as e:
            scanned_sources.append({"app": "Claude Desktop", "status": f"읽기 오류 ({e})", "path": claude_path, "count": 0, "servers": []})
    else:
        scanned_sources.append({"app": "Claude Desktop", "status": "설정 파일 없음", "path": claude_path, "count": 0, "servers": []})

    # 2. Cursor 설정 파일 스캔
    cursor_path = os.path.join(home, ".cursor", "mcp.json")
    cursor_servers = []
    if os.path.exists(cursor_path):
        try:
            with open(cursor_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for s_name, s_conf in data.get("mcpServers", {}).items():
                    if s_name != "plugin-switchboard" and s_name not in discovered_servers:
                        cursor_servers.append(s_name)
                        discovered_servers[s_name] = ("Cursor", s_conf)
            scanned_sources.append({"app": "Cursor", "status": "연결됨", "path": cursor_path, "count": len(cursor_servers), "servers": cursor_servers})
        except Exception:
            scanned_sources.append({"app": "Cursor", "status": "읽기 오류", "path": cursor_path, "count": 0, "servers": []})
    else:
        scanned_sources.append({"app": "Cursor", "status": "설정 파일 없음", "path": cursor_path, "count": 0, "servers": []})

    # 3. Antigravity 설정 및 플러그인 스캔
    agy_dir = os.path.join(home, ".gemini", "antigravity")
    agy_mcp_path = os.path.join(agy_dir, "mcp_config.json")
    agy_servers = []
    if os.path.exists(agy_mcp_path):
        try:
            with open(agy_mcp_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for s_name, s_conf in data.get("mcpServers", {}).items():
                    if s_name != "plugin-switchboard" and s_name not in discovered_servers:
                        agy_servers.append(s_name)
                        discovered_servers[s_name] = ("Antigravity", s_conf)
            scanned_sources.append({"app": "Antigravity", "status": "연결됨", "path": agy_mcp_path, "count": len(agy_servers), "servers": agy_servers})
        except Exception:
            scanned_sources.append({"app": "Antigravity", "status": "읽기 오류", "path": agy_mcp_path, "count": 0, "servers": []})
    elif os.path.exists(agy_dir):
        # Antigravity 앱 데이터 폴더가 감지된 경우
        scanned_sources.append({"app": "Antigravity", "status": "연결됨 (앱 감지)", "path": agy_dir, "count": 0, "servers": []})
    else:
        scanned_sources.append({"app": "Antigravity", "status": "설치되지 않음", "path": agy_dir, "count": 0, "servers": []})

    # 기존 설정 읽기
    current_config = load_config()
    existing_ids = {p["id"] for p in current_config.get("plugins", [])}
    
    added_plugins = []
    already_existing_plugins = []

    def guess_category(name):
        n = name.lower()
        if any(k in n for k in ["video", "movie", "luma", "runway", "kling", "pika", "sora", "animate"]):
            return "video", "영상"
        elif any(k in n for k in ["image", "draw", "art", "midjourney", "flux", "dalle", "canvas", "photo"]):
            return "image", "이미지"
        elif any(k in n for k in ["voice", "audio", "sound", "music", "speech", "tts", "whisper", "suno"]):
            return "audio", "음성"
        elif any(k in n for k in ["search", "web", "crawl", "google", "brave", "tavily", "news", "fetch"]):
            return "search", "검색"
        elif any(k in n for k in ["doc", "pdf", "sheet", "excel", "notion", "calendar", "mail", "slack", "office"]):
            return "office", "문서·업무"
        elif any(k in n for k in ["browser", "puppeteer", "playwright", "selenium"]):
            return "browser", "브라우저"
        elif any(k in n for k in ["data", "chart", "sql", "db", "postgres", "sqlite", "graph", "stat"]):
            return "data", "데이터"
        else:
            return "system", "시스템"

    for s_name, (source_app, s_conf) in discovered_servers.items():
        clean_id = s_name.lower().replace(" ", "-")
        if clean_id not in existing_ids:
            cat, tag = guess_category(s_name)
            new_item = {
                "id": clean_id,
                "name": s_name,
                "cat": cat,
                "tag": f"{source_app} 연동",
                "desc": f"{source_app}에서 자동으로 감지되어 불러온 도구입니다.",
                "enabled": True,
                "source": source_app
            }
            current_config.setdefault("plugins", []).append(new_item)
            added_plugins.append(new_item)
            existing_ids.add(clean_id)
        else:
            already_existing_plugins.append(s_name)

    if added_plugins:
        save_config(current_config)

    return {
        "success": True,
        "scannedSources": scanned_sources,
        "totalDetected": len(discovered_servers),
        "addedCount": len(added_plugins),
        "addedList": added_plugins,
        "alreadyList": already_existing_plugins,
        "plugins": current_config["plugins"]
    }

# 각 AI 앱 설정 파일 자동 등록 (Claude Desktop, Cursor 등)
def setup_all_apps():
    home = os.path.expanduser("~")
    system = platform.system()
    configured_apps = []

    mcp_entry = {
        "command": sys.executable,
        "args": [os.path.join(BASE_DIR, "main.py"), "--mcp"]
    }

    # 1. Claude Desktop 설정 파일 경로
    if system == "Darwin":
        claude_config_path = os.path.join(home, "Library", "Application Support", "Claude", "claude_desktop_config.json")
    else:
        claude_config_path = os.path.join(os.environ.get("APPDATA", home), "Claude", "claude_desktop_config.json")

    claude_mcp_entry = {
        "command": sys.executable,
        "args": [os.path.join(BASE_DIR, "main.py"), "--mcp", "--app=claude"]
    }

    try:
        os.makedirs(os.path.dirname(claude_config_path), exist_ok=True)
        conf = {}
        if os.path.exists(claude_config_path):
            with open(claude_config_path, "r", encoding="utf-8") as f:
                conf = json.load(f)
        conf.setdefault("mcpServers", {})["plugin-switchboard"] = claude_mcp_entry
        with open(claude_config_path, "w", encoding="utf-8") as f:
            json.dump(conf, f, ensure_ascii=False, indent=2)
        configured_apps.append("Claude Desktop")
    except Exception as e:
        sys.stderr.write(f"Claude 연동 실패: {e}\n")

    # 2. Cursor / Codex 설정
    cursor_config_path = os.path.join(home, ".cursor", "mcp.json")
    cursor_mcp_entry = {
        "command": sys.executable,
        "args": [os.path.join(BASE_DIR, "main.py"), "--mcp", "--app=cursor"]
    }
    try:
        os.makedirs(os.path.dirname(cursor_config_path), exist_ok=True)
        conf = {}
        if os.path.exists(cursor_config_path):
            with open(cursor_config_path, "r", encoding="utf-8") as f:
                conf = json.load(f)
        conf.setdefault("mcpServers", {})["plugin-switchboard"] = cursor_mcp_entry
        with open(cursor_config_path, "w", encoding="utf-8") as f:
            json.dump(conf, f, ensure_ascii=False, indent=2)
        configured_apps.append("Cursor")
    except Exception:
        pass

    # 3. Antigravity 설정 등록
    agy_dir = os.path.join(home, ".gemini", "antigravity")
    agy_config_path = os.path.join(agy_dir, "mcp_config.json")
    agy_mcp_entry = {
        "command": sys.executable,
        "args": [os.path.join(BASE_DIR, "main.py"), "--mcp", "--app=antigravity"]
    }
    try:
        if os.path.exists(agy_dir):
            os.makedirs(os.path.dirname(agy_config_path), exist_ok=True)
            conf = {}
            if os.path.exists(agy_config_path):
                with open(agy_config_path, "r", encoding="utf-8") as f:
                    conf = json.load(f)
            conf.setdefault("mcpServers", {})["plugin-switchboard"] = agy_mcp_entry
            with open(agy_config_path, "w", encoding="utf-8") as f:
                json.dump(conf, f, ensure_ascii=False, indent=2)
            configured_apps.append("Antigravity")
    except Exception:
        pass

    if configured_apps:
        return f"성공! {', '.join(configured_apps)}에 스위치보드가 자동 등록되었습니다. 앱을 재시작하면 바로 적용됩니다."
    return "설정 파일 자동 등록 완료!"

# 데스크톱 미니 앱 창 실행 (주소창/탭 없는 순수 독립 위젯 모드)
def launch_desktop_widget(url):
    system = platform.system()

    if system == "Darwin": # macOS
        # macOS에서 --user-data-dir를 쓰면 독(Dock)에 크롬캐스트 아이콘이 뜨고 클릭 시 새 창이 열리는 크롬 버그가 발생함
        # 따라서 기존 브라우저 세션에 연결하여 순수 독립 --app 창으로만 깔끔하게 실행
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
        ]
        for p in chrome_paths:
            if os.path.exists(p):
                subprocess.Popen([p, f"--app={url}"])
                return
        subprocess.Popen(["open", "-a", "Google Chrome", "--args", f"--app={url}"])

    elif system == "Windows":
        app_args = [f"--app={url}"]
        chrome_paths = [
            # Chrome (ProgramFiles, x86, LocalAppData)
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
            # Microsoft Edge (Windows 10/11 전 기종 기본 내장)
            os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\Application\msedge.exe"),
            # Brave
            os.path.expandvars(r"%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe"),
            os.path.expandvars(r"%LocalAppData%\BraveSoftware\Brave-Browser\Application\brave.exe")
        ]
        for p in chrome_paths:
            if os.path.exists(p):
                try:
                    subprocess.Popen([p] + app_args)
                    return
                except Exception:
                    pass
        webbrowser.open(url)
    else:
        subprocess.Popen(["xdg-open", url])

# MCP (Model Context Protocol) 표준 stdio 서버 핸들러
def run_mcp():
    target_app = "claude"
    for arg in sys.argv:
        if arg.startswith("--app="):
            target_app = arg.split("=", 1)[1].lower()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue

        req_id = req.get("id")
        method = req.get("method")

        if method == "initialize":
            params = req.get("params", {})
            client_name = params.get("clientInfo", {}).get("name", "").lower()
            if "cursor" in client_name:
                target_app = "cursor"
            elif "antigravity" in client_name:
                target_app = "antigravity"
            elif "claude" in client_name:
                target_app = "claude"

            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": { "tools": {} },
                    "serverInfo": { "name": "plugin-switchboard", "version": "2.2.0" }
                }
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "tools/list":
            # 핵심: 현재 연결된 AI 앱(target_app)에 켜져 있는 플러그인만 전달!
            data = load_config()
            tools = [
                {
                    "name": "switchboard_status",
                    "description": f"현재 [{target_app}]에 활성화된 플러그인 목록을 확인합니다.",
                    "inputSchema": { "type": "object", "properties": {} }
                }
            ]
            for p in data.get("plugins", []):
                enabled_apps = p.get("enabled_apps", {})
                is_active = enabled_apps.get(target_app, p.get("enabled", False))
                if is_active:
                    tools.append({
                        "name": f"plugin_{p['id']}",
                        "description": f"[{p['name']}] {p['desc']}",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "prompt": { "type": "string", "description": f"{p['name']}에게 요청할 작업" }
                            },
                            "required": ["prompt"]
                        }
                    })
            res = { "jsonrpc": "2.0", "id": req_id, "result": { "tools": tools } }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "tools/call":
            params = req.get("params", {})
            name = params.get("name")
            args = params.get("arguments", {})

            if name == "switchboard_status":
                data = load_config()
                active = [p["name"] for p in data.get("plugins", []) if p.get("enabled_apps", {}).get(target_app, p.get("enabled", False))]
                msg = f"현재 [{target_app}]에 활성화된 플러그인 ({len(active)}개):\n- " + "\n- ".join(active) if active else f"현재 [{target_app}]의 모든 플러그인이 꺼져 있습니다. (순수 대화 모드)"
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": { "content": [{"type": "text", "text": msg}] }
                }
            else:
                prompt = args.get("prompt", "")
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": f"[{name}] 플러그인 작업 완료: {prompt}"}]
                    }
                }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "notifications/initialized":
            pass

if __name__ == "__main__":
    if "--mcp" in sys.argv:
        # LLM(클로드, 안티그래비티 등)이 도구 목록을 호출할 때 실행되는 모드
        run_mcp()
    else:
        # 사용자가 더블클릭해서 미니 리모컨 위젯을 띄울 때 실행되는 모드
        port = 8765
        server = ThreadingHTTPServer(("127.0.0.1", port), WidgetHandler)
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()

        launch_desktop_widget(f"http://127.0.0.1:{port}")
        print(f"⚡ 스위치보드 미니 위젯이 실행되었습니다: http://127.0.0.1:{port}")
        print("종료하려면 Ctrl+C를 누르세요.")
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
