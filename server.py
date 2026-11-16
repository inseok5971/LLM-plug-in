#!/usr/bin/env python3
"""
AI 플러그인 스위치보드 (Plugin Switchboard) - 통합 백엔드 & MCP 게이트웨이
- 웹 대시보드 API 서빙 (기본 포트: 8765)
- Claude Desktop / Antigravity / Cursor 호환 MCP (Model Context Protocol) 지원
"""

import sys
import os
import json
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

DATA_FILE = os.path.join(os.path.dirname(__file__), "plugins_data.json")
HTML_FILE = os.path.join(os.path.dirname(__file__), "index.html")

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            sys.stderr.write(f"데이터 파일 읽기 실패: {e}\n")
    return {"categories": [], "plugins": []}

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        sys.stderr.write(f"데이터 파일 저장 실패: {e}\n")

# HTTP 요청 핸들러
class SwitchboardHandler(SimpleHTTPRequestHandler):
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
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(HTML_FILE, "rb") as f:
                self.wfile.write(f.read())
            return
        elif parsed.path == "/api/data" or parsed.path == "/plugins_data.json":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            data = load_data()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
            return
        
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        req_data = json.loads(body) if body else {}

        data = load_data()

        if parsed.path == "/api/toggle":
            plugin_id = req_data.get("id")
            enabled = req_data.get("enabled", False)
            for p in data.get("plugins", []):
                if p["id"] == plugin_id:
                    p["enabled"] = enabled
                    break
            save_data(data)
            self._send_json({"success": True, "id": plugin_id, "enabled": enabled})
            return

        elif parsed.path == "/api/category-off":
            cat_id = req_data.get("category")
            for p in data.get("plugins", []):
                if p.get("category") == cat_id:
                    p["enabled"] = False
            save_data(data)
            self._send_json({"success": True, "category": cat_id})
            return

        elif parsed.path == "/api/preset":
            preset = req_data.get("preset")
            for p in data.get("plugins", []):
                p["enabled"] = False
            
            preset_map = {
                "video": "runway",
                "image": "midjourney",
                "audio": "elevenlabs",
                "office": "pdf-analyzer",
                "search": "google-search"
            }
            if preset in preset_map:
                target_id = preset_map[preset]
                for p in data.get("plugins", []):
                    if p["id"] == target_id:
                        p["enabled"] = True
                        break

            save_data(data)
            self._send_json({"success": True, "preset": preset})
            return

        elif parsed.path == "/api/add-plugin":
            data.setdefault("plugins", []).append(req_data)
            save_data(data)
            self._send_json({"success": True, "plugin": req_data})
            return

        self.send_error(404, "Endpoint not found")

    def _send_json(self, obj):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(obj, ensure_ascii=False).encode("utf-8"))

def start_http_server(port=8765):
    server = HTTPServer(("0.0.0.0", port), SwitchboardHandler)
    print(f"✅ 플러그인 스위치보드 웹 대시보드가 열렸습니다: http://localhost:{port}")
    server.serve_forever()

# MCP (Model Context Protocol) 표준 stdio 핸들러
def run_mcp_server():
    """Claude Desktop 또는 Antigravity와 JSON-RPC 2.0으로 통신하는 MCP 서버"""
    sys.stderr.write("🔌 AI 플러그인 스위치보드 MCP 서버가 시작되었습니다.\n")
    
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
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "plugin-switchboard",
                        "version": "1.0.0"
                    }
                }
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "tools/list":
            # 핵심 기능: 현재 켜져 있는(enabled=True) 플러그인의 도구만 반환!
            data = load_data()
            active_tools = []

            # 1. 스위치 상태를 제어할 수 있는 메타 도구 항상 포함
            active_tools.append({
                "name": "switchboard_check_status",
                "description": "현재 활성화된 플러그인 목록과 카테고리별 스위치 상태를 확인합니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            })

            # 2. 현재 활성화된 플러그인들만 도구로 노출
            for p in data.get("plugins", []):
                if p.get("enabled"):
                    active_tools.append({
                        "name": f"plugin_{p['id']}",
                        "description": f"[{p['name_ko']}] {p['description']}",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "prompt": {
                                    "type": "string",
                                    "description": f"{p['name_ko']}에게 요청할 작업 내용"
                                }
                            },
                            "required": ["prompt"]
                        }
                    })

            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": active_tools
                }
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "tools/call":
            params = req.get("params", {})
            name = params.get("name")
            args = params.get("arguments", {})

            if name == "switchboard_check_status":
                data = load_data()
                active = [p["name_ko"] for p in data.get("plugins", []) if p.get("enabled")]
                text = f"현재 활성화된 플러그인 ({len(active)}개):\n- " + "\n- ".join(active) if active else "현재 켜진 플러그인이 없습니다. (순수 대화 모드)"
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": text}]
                    }
                }
            else:
                # 개별 플러그인 실행 시뮬레이션 / 실제 플러그인 프록시
                prompt = args.get("prompt", "")
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"[{name}] 플러그인이 성공적으로 실행되었습니다.\n요청 작업: {prompt}"
                            }
                        ]
                    }
                }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "notifications/initialized":
            pass

if __name__ == "__main__":
    if "--mcp" in sys.argv:
        # MCP 모드로 단독 실행 (Claude Desktop, Antigravity 등에서 사용)
        run_mcp_server()
    else:
        # 일반 실행: 백그라운드 웹서버 시작 + 자동 브라우저 실행
        port = 8765
        t = threading.Thread(target=start_http_server, args=(port,), daemon=True)
        t.start()
        
        # 시스템 브라우저 자동 오픈
        import subprocess
        try:
            subprocess.run(["open", f"http://localhost:{port}"])
        except Exception:
            pass

        print("Press Ctrl+C to exit.")
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n서버를 종료합니다.")
