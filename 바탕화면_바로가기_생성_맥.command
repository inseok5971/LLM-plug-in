#!/bin/bash
# 맥(macOS) 전용 바탕화면 바로가기 앱 생성기
cd "$(dirname "$0")"
CURRENT_DIR="$(pwd)"
DESKTOP="$HOME/Desktop"
APP_DIR="$DESKTOP/AI 플러그인 스위치보드.app"

echo "=========================================================="
echo " ⚡ 맥 바탕화면에 'AI 플러그인 스위치보드' 앱을 생성합니다..."
echo "=========================================================="

mkdir -p "$APP_DIR/Contents/MacOS" "$APP_DIR/Contents/Resources"

cat << EOF > "$APP_DIR/Contents/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundleIdentifier</key>
    <string>com.switchboard.ai</string>
    <key>CFBundleName</key>
    <string>AI 플러그인 스위치보드</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>2.2</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
</dict>
</plist>
EOF

cat << EOF > "$APP_DIR/Contents/MacOS/launcher"
#!/bin/bash
cd "$CURRENT_DIR" || exit 1
lsof -ti:8765 | xargs kill -9 2>/dev/null
exec python3 main.py
EOF

chmod +x "$APP_DIR/Contents/MacOS/launcher"

ICON_PATH="/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/ToolbarCustomizeIcon.icns"
if [ ! -f "$ICON_PATH" ]; then
    ICON_PATH="/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/GenericApplicationIcon.icns"
fi
cp "$ICON_PATH" "$APP_DIR/Contents/Resources/AppIcon.icns" 2>/dev/null || true
touch "$APP_DIR"

mkdir -p "$HOME/Applications"
cp -R "$APP_DIR" "$HOME/Applications/" 2>/dev/null || true

echo ""
echo "✅ 맥 바탕화면 및 응용 프로그램(Applications)에 앱 생성이 완료되었습니다!"
echo "앞으로는 바탕화면의 [AI 플러그인 스위치보드] 아이콘만 더블 클릭하시면 바로 실행됩니다."
echo ""
sleep 2
