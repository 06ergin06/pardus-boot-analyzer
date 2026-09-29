#!/bin/bash
# AppImage Packaging Script for Pardus Boot Analyzer
set -e

PKG_NAME="pardus-boot-analyzer"
APP_DIR="AppDir"
OUTPUT_IMAGE="Pardus_Boot_Analyzer-x86_64.AppImage"

echo "Creating clean AppDir structure..."
rm -rf "$APP_DIR"
mkdir -p "$APP_DIR/usr/share/$PKG_NAME"
mkdir -p "$APP_DIR/usr/share/applications"
mkdir -p "$APP_DIR/usr/share/icons/hicolor/scalable/apps"
mkdir -p "$APP_DIR/usr/share/pixmaps"
mkdir -p "$APP_DIR/usr/lib/girepository-1.0"
mkdir -p "$APP_DIR/usr/lib"
mkdir -p "$APP_DIR/usr/share/glib-2.0/schemas"
mkdir -p "$APP_DIR/usr/lib/python3/site-packages"

echo "Copying application files..."
cp -r main.py "$APP_DIR/usr/share/$PKG_NAME/"
cp -r src "$APP_DIR/usr/share/$PKG_NAME/"
cp -r ui "$APP_DIR/usr/share/$PKG_NAME/"
cp -r locale "$APP_DIR/usr/share/$PKG_NAME/"
cp pardus-boot-analyzer.svg "$APP_DIR/usr/share/$PKG_NAME/"

# Remove pycache if any
find "$APP_DIR" -type d -name "__pycache__" -exec rm -rf {} + || true

echo "Installing desktop entry..."
cp pardus-boot-analyzer.desktop "$APP_DIR/usr/share/applications/$PKG_NAME.desktop"
cp pardus-boot-analyzer.desktop "$APP_DIR/$PKG_NAME.desktop"

echo "Copying application icon..."
cp pardus-boot-analyzer.svg "$APP_DIR/usr/share/icons/hicolor/scalable/apps/$PKG_NAME.svg"
cp pardus-boot-analyzer.svg "$APP_DIR/usr/share/pixmaps/$PKG_NAME.svg"
cp pardus-boot-analyzer.svg "$APP_DIR/$PKG_NAME.svg"
cp pardus-boot-analyzer.svg "$APP_DIR/.DirIcon"

echo "Bundling GObject Introspection typelibs..."
TYPELIB_DIRS=(
    "/usr/lib/girepository-1.0"
    "/usr/lib64/girepository-1.0"
    "/usr/lib/x86_64-linux-gnu/girepository-1.0"
)

TYPELIBS=(
    "Gtk-3.0.typelib"
    "Gdk-3.0.typelib"
    "GLib-2.0.typelib"
    "GObject-2.0.typelib"
    "Pango-1.0.typelib"
    "PangoCairo-1.0.typelib"
    "PangoFT2-1.0.typelib"
    "cairo-1.0.typelib"
    "Atk-1.0.typelib"
    "GdkPixbuf-2.0.typelib"
    "Gio-2.0.typelib"
    "GModule-2.0.typelib"
    "HarfBuzz-0.0.typelib"
    "xlib-2.0.typelib"
    "GdkX11-3.0.typelib"
)

for tdir in "${TYPELIB_DIRS[@]}"; do
    if [ -d "$tdir" ]; then
        echo "Found system typelib path at $tdir"
        for tfile in "${TYPELIBS[@]}"; do
            if [ -f "$tdir/$tfile" ]; then
                cp -L "$tdir/$tfile" "$APP_DIR/usr/lib/girepository-1.0/"
            fi
        done
        break
    fi
done

echo "Bundling GTK3 and core dependencies..."
LIB_DIRS=(
    "/usr/lib"
    "/usr/lib64"
    "/usr/lib/x86_64-linux-gnu"
)

SHARED_LIBS=(
    "libgtk-3.so*"
    "libgdk-3.so*"
    "libgirepository-*.so*"
    "libglib-2.0.so*"
    "libgobject-2.0.so*"
    "libgio-2.0.so*"
    "libgmodule-2.0.so*"
    "libpango-1.0.so*"
    "libpangocairo-1.0.so*"
    "libgdk_pixbuf-2.0.so*"
    "libcairo.so*"
    "libcairo-gobject.so*"
    "libatk-1.0.so*"
    "libatk-bridge-2.0.so*"
    "libatspi.so*"
    "libepoxy.so*"
    "libharfbuzz.so*"
    "libfribidi.so*"
    "libfontconfig.so*"
    "libfreetype.so*"
    "libpixman-1.so*"
    "libtinysparql-*.so*"
    "libcloudproviders.so*"
)

for ldir in "${LIB_DIRS[@]}"; do
    if [ -d "$ldir" ] && [ -e "$ldir/libgtk-3.so.0" ]; then
        echo "Found system libraries path at $ldir"
        for pattern in "${SHARED_LIBS[@]}"; do
            for match in $ldir/$pattern; do
                if [ -e "$match" ]; then
                    cp -d "$match" "$APP_DIR/usr/lib/" 2>/dev/null || true
                fi
            done
        done
        if [ -d "$ldir/gtk-3.0" ]; then
            cp -r "$ldir/gtk-3.0" "$APP_DIR/usr/lib/" 2>/dev/null || true
        fi
        break
    fi
done

if [ -d "/usr/share/glib-2.0/schemas" ]; then
    echo "Bundling GSettings schemas..."
    cp -r /usr/share/glib-2.0/schemas/* "$APP_DIR/usr/share/glib-2.0/schemas/" 2>/dev/null || true
fi

echo "Bundling Python PyGObject bindings..."
for pdir in /usr/lib/python3*/site-packages /usr/lib/python3*/dist-packages; do
    if [ -d "$pdir/gi" ]; then
        echo "Found Python gi package at $pdir"
        cp -r "$pdir/gi" "$APP_DIR/usr/lib/python3/site-packages/" 2>/dev/null || true
        if [ -d "$pdir/cairo" ]; then
            cp -r "$pdir/cairo" "$APP_DIR/usr/lib/python3/site-packages/" 2>/dev/null || true
        fi
        break
    fi
done

echo "Creating AppRun entrypoint..."
cat << 'EOF' > "$APP_DIR/AppRun"
#!/bin/sh
SELF=$(readlink -f "$0")
HERE=$(dirname "$SELF")

# Base AppDir path
export APPDIR="$HERE"

# Shared library search path (prioritize bundled libraries)
export LD_LIBRARY_PATH="$HERE/usr/lib:$HERE/usr/lib64:$HERE/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

# GObject Introspection typelib path
export GI_TYPELIB_PATH="$HERE/usr/lib/girepository-1.0:$HERE/usr/lib64/girepository-1.0:$HERE/usr/lib/x86_64-linux-gnu/girepository-1.0:${GI_TYPELIB_PATH:+:$GI_TYPELIB_PATH}"

# Python module search path
export PYTHONPATH="$HERE/usr/share/pardus-boot-analyzer:$HERE/usr/lib/python3/site-packages:$HERE/usr/lib/python3/dist-packages:${PYTHONPATH:+:$PYTHONPATH}"

# GSettings schemas path
if [ -d "$HERE/usr/share/glib-2.0/schemas" ]; then
    export GSETTINGS_SCHEMA_DIR="$HERE/usr/share/glib-2.0/schemas:${GSETTINGS_SCHEMA_DIR:+:$GSETTINGS_SCHEMA_DIR}"
fi

# GTK3 modules path
if [ -d "$HERE/usr/lib/gtk-3.0" ]; then
    export GTK_PATH="$HERE/usr/lib/gtk-3.0:${GTK_PATH:+:$GTK_PATH}"
fi

# XDG data directories for icons and themes
export XDG_DATA_DIRS="$HERE/usr/share:${XDG_DATA_DIRS:+:$XDG_DATA_DIRS}"

# Execute application using host python3
exec python3 "$HERE/usr/share/pardus-boot-analyzer/main.py" "$@"
EOF
chmod +x "$APP_DIR/AppRun"

echo "Locating appimagetool..."
TOOL_PATH=""
if command -v appimagetool >/dev/null 2>&1; then
    TOOL_PATH="$(command -v appimagetool)"
    echo "Found system appimagetool at $TOOL_PATH"
elif [ -f "/home/ergin/Projects/python_gtk/appimagetool" ] && [ -x "/home/ergin/Projects/python_gtk/appimagetool" ]; then
    TOOL_PATH="/home/ergin/Projects/python_gtk/appimagetool"
    echo "Found local appimagetool at $TOOL_PATH"
elif [ -f "./appimagetool-x86_64.AppImage" ] && [ -x "./appimagetool-x86_64.AppImage" ]; then
    TOOL_PATH="./appimagetool-x86_64.AppImage"
    echo "Found local appimagetool at $TOOL_PATH"
else
    TOOL_PATH="./appimagetool-x86_64.AppImage"
    echo "Local tool not found, downloading latest appimagetool from GitHub releases..."
    curl -L -o "$TOOL_PATH" "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x "$TOOL_PATH"
fi

echo "Building AppImage..."
ARCH=x86_64 "$TOOL_PATH" "$APP_DIR" "$OUTPUT_IMAGE"

echo "Cleaning up AppDir..."
rm -rf "$APP_DIR"

echo "===================================================="
echo "AppImage successfully built:"
echo "-> $OUTPUT_IMAGE"
echo ""
echo "You can run it on any system using:"
echo "   ./$OUTPUT_IMAGE"
echo "===================================================="
