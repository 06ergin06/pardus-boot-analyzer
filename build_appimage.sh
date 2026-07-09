#!/bin/bash
# AppImage Packaging Script for Pardus Boot Analyzer
set -e

PKG_NAME="pardus-boot-analyzer"
APP_DIR="AppDir"

echo "Creating clean AppDir structure..."
rm -rf "$APP_DIR"
mkdir -p "$APP_DIR/usr/share/$PKG_NAME"
mkdir -p "$APP_DIR/usr/share/applications"
mkdir -p "$APP_DIR/usr/share/icons/hicolor/48x48/apps"

echo "Copying application files..."
cp -r main.py "$APP_DIR/usr/share/$PKG_NAME/"
cp -r src "$APP_DIR/usr/share/$PKG_NAME/"
cp -r ui "$APP_DIR/usr/share/$PKG_NAME/"

# Remove pycache
find "$APP_DIR" -type d -name "__pycache__" -exec rm -rf {} + || true

echo "Creating desktop entry..."
cat << EOF > "$APP_DIR/usr/share/applications/$PKG_NAME.desktop"
[Desktop Entry]
Name=Pardus Başlangıç Yöneticisi
Name[en]=Pardus Boot Analyzer
Comment=Sistem açılış süresini analiz et ve başlangıç programlarını yönet
Comment[en]=Analyze system boot time and manage startup applications
Exec=pardus-boot-analyzer
Icon=utilities-system-monitor
Terminal=false
Type=Application
Categories=System;Settings;GTK;
StartupNotify=true
EOF

# Copy desktop file to root of AppDir
cp "$APP_DIR/usr/share/applications/$PKG_NAME.desktop" "$APP_DIR/"

echo "Locating and copying icon..."
ICON_SRC=""
# Try standard icon paths
for path in \
    "/usr/share/icons/AdwaitaLegacy/48x48/legacy/utilities-system-monitor.png" \
    "/usr/share/icons/HighContrast/48x48/apps/utilities-system-monitor.png" \
    "/usr/share/icons/hicolor/48x48/apps/utilities-system-monitor.png"; do
    if [ -f "$path" ]; then
        ICON_SRC="$path"
        break
    fi
done

if [ -z "$ICON_SRC" ]; then
    echo "Warning: utilities-system-monitor.png not found. Using generic fallback icon."
    # Create a dummy image or copy another standard one
    ICON_SRC="/usr/share/icons/AdwaitaLegacy/16x16/legacy/utilities-system-monitor.png"
fi

if [ -f "$ICON_SRC" ]; then
    cp "$ICON_SRC" "$APP_DIR/usr/share/icons/hicolor/48x48/apps/utilities-system-monitor.png"
    cp "$ICON_SRC" "$APP_DIR/utilities-system-monitor.png"
fi

echo "Creating AppRun entrypoint..."
cat << 'EOF' > "$APP_DIR/AppRun"
#!/bin/sh
SELF=$(readlink -f "$0")
HERE=$(dirname "$SELF")

# Run main.py using host python3
exec python3 "$HERE/usr/share/pardus-boot-analyzer/main.py" "$@"
EOF
chmod +x "$APP_DIR/AppRun"

echo "Locating appimagetool..."
TOOL_PATH="/home/ergin/Projects/python_gtk/appimagetool"
if [ -f "$TOOL_PATH" ] && [ -x "$TOOL_PATH" ]; then
    echo "Found local appimagetool at $TOOL_PATH"
else
    TOOL_PATH="./appimagetool-x86_64.AppImage"
    if [ ! -f "$TOOL_PATH" ]; then
        echo "Local tool not found, downloading appimagetool from GitHub releases..."
        curl -L -o "$TOOL_PATH" "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"
        chmod +x "$TOOL_PATH"
    fi
fi

echo "Building AppImage..."
# Run tool with ARCH environment variable
ARCH=x86_64 "$TOOL_PATH" "$APP_DIR" "Pardus_Boot_Analyzer-x86_64.AppImage"

echo "Cleaning up AppDir..."
rm -rf "$APP_DIR"

echo "===================================================="
echo "AppImage successfully built:"
echo "-> Pardus_Boot_Analyzer-x86_64.AppImage"
echo ""
echo "You can run it on any system using:"
echo "   ./Pardus_Boot_Analyzer-x86_64.AppImage"
echo "===================================================="
