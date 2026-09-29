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
    "/lib/x86_64-linux-gnu"
    "/lib64"
    "/lib"
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
    "libpangoft2-1.0.so*"
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
    "libpcre*.so*"
    "libffi*.so*"
    "libselinux*.so*"
    "libmount*.so*"
    "libblkid*.so*"
    "libz*.so*"
    "libbz2*.so*"
    "libpng*.so*"
    "libexpat*.so*"
    "libthai*.so*"
    "libdatrie*.so*"
    "libgraphite2*.so*"
    "librsvg-2.so*"
)

for ldir in "${LIB_DIRS[@]}"; do
    if [ -d "$ldir" ]; then
        echo "Searching libraries in $ldir..."
        for pattern in "${SHARED_LIBS[@]}"; do
            for match in $ldir/$pattern; do
                if [ -e "$match" ]; then
                    if [ -L "$match" ]; then
                        real_target=$(readlink -f "$match" 2>/dev/null || true)
                        if [ -f "$real_target" ]; then
                            cp -d "$real_target" "$APP_DIR/usr/lib/" 2>/dev/null || true
                        fi
                    fi
                    cp -d "$match" "$APP_DIR/usr/lib/" 2>/dev/null || true
                fi
            done
        done
        if [ -d "$ldir/gtk-3.0" ] && [ ! -d "$APP_DIR/usr/lib/gtk-3.0" ]; then
            cp -r "$ldir/gtk-3.0" "$APP_DIR/usr/lib/" 2>/dev/null || true
        fi
    fi
done

if [ -d "/usr/share/glib-2.0/schemas" ]; then
    echo "Bundling GSettings schemas..."
    cp -r /usr/share/glib-2.0/schemas/* "$APP_DIR/usr/share/glib-2.0/schemas/" 2>/dev/null || true
fi

echo "Bundling Python runtime, standard library, and bindings..."
mkdir -p "$APP_DIR/usr/bin"
PYTHON_BIN="$(command -v python3)"
cp -L "$PYTHON_BIN" "$APP_DIR/usr/bin/python3"
chmod +x "$APP_DIR/usr/bin/python3"

PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_STDLIB=$(python3 -c "import sysconfig; print(sysconfig.get_path('stdlib'))")

# Bundle libpython shared library
for ldir in "${LIB_DIRS[@]}"; do
    if [ -d "$ldir" ]; then
        for match in "$ldir"/libpython"${PYTHON_VER}"*.so*; do
            if [ -e "$match" ]; then
                if [ -L "$match" ]; then
                    real_target=$(readlink -f "$match" 2>/dev/null || true)
                    if [ -f "$real_target" ]; then
                        cp -d "$real_target" "$APP_DIR/usr/lib/" 2>/dev/null || true
                    fi
                fi
                cp -d "$match" "$APP_DIR/usr/lib/" 2>/dev/null || true
            fi
        done
    fi
done

# Bundle Python standard library modules (strictly excluding site-packages, test suites, and caches)
mkdir -p "$APP_DIR/usr/lib/python${PYTHON_VER}"
if [ -d "$PYTHON_STDLIB" ]; then
    echo "Copying standard library from $PYTHON_STDLIB..."
    if command -v rsync >/dev/null 2>&1; then
        rsync -a \
            --exclude="site-packages" \
            --exclude="dist-packages" \
            --exclude="test" \
            --exclude="tests" \
            --exclude="idlelib" \
            --exclude="tkinter" \
            --exclude="turtle*" \
            --exclude="__pycache__" \
            "$PYTHON_STDLIB/" "$APP_DIR/usr/lib/python${PYTHON_VER}/" 2>/dev/null || true
    else
        cp -r "$PYTHON_STDLIB"/* "$APP_DIR/usr/lib/python${PYTHON_VER}/" 2>/dev/null || true
        rm -rf "$APP_DIR/usr/lib/python${PYTHON_VER}"/site-packages "$APP_DIR/usr/lib/python${PYTHON_VER}"/dist-packages "$APP_DIR/usr/lib/python${PYTHON_VER}"/test "$APP_DIR/usr/lib/python${PYTHON_VER}"/tests 2>/dev/null || true
    fi
fi

# Bundle Python PyGObject and cairo packages
mkdir -p "$APP_DIR/usr/lib/python${PYTHON_VER}/site-packages"
for pdir in /usr/lib/python3*/site-packages /usr/lib/python3*/dist-packages /usr/local/lib/python3*/site-packages /usr/local/lib/python3*/dist-packages; do
    if [ -d "$pdir/gi" ]; then
        echo "Found Python gi package at $pdir"
        cp -r "$pdir/gi" "$APP_DIR/usr/lib/python${PYTHON_VER}/site-packages/" 2>/dev/null || true
        if [ -d "$pdir/cairo" ]; then
            cp -r "$pdir/cairo" "$APP_DIR/usr/lib/python${PYTHON_VER}/site-packages/" 2>/dev/null || true
        fi
        break
    fi
done

# Create compatibility symlinks for python3/site-packages and python3/dist-packages
mkdir -p "$APP_DIR/usr/lib/python3"
ln -sf "../python${PYTHON_VER}/site-packages" "$APP_DIR/usr/lib/python3/site-packages" 2>/dev/null || true
ln -sf "../python${PYTHON_VER}/site-packages" "$APP_DIR/usr/lib/python3/dist-packages" 2>/dev/null || true

echo "Bundling icon themes..."
mkdir -p "$APP_DIR/usr/share/icons"
if [ -d "/usr/share/icons/hicolor" ]; then
    echo "Copying hicolor icon theme..."
    cp -r /usr/share/icons/hicolor "$APP_DIR/usr/share/icons/" 2>/dev/null || true
fi
if [ -d "/usr/share/icons/Adwaita" ]; then
    echo "Copying Adwaita icon theme..."
    cp -r /usr/share/icons/Adwaita "$APP_DIR/usr/share/icons/" 2>/dev/null || true
fi

echo "Bundling GdkPixbuf loaders and generating loaders.cache..."
mkdir -p "$APP_DIR/usr/lib/gdk-pixbuf-2.0/loaders"

LOADER_DIRS=(
    /usr/lib/x86_64-linux-gnu/gdk-pixbuf-2.0/*/loaders
    /usr/lib/x86_64-linux-gnu/gdk-pixbuf-2.0/loaders
    /usr/lib/gdk-pixbuf-2.0/*/loaders
    /usr/lib/gdk-pixbuf-2.0/loaders
    /usr/lib64/gdk-pixbuf-2.0/*/loaders
    /usr/lib64/gdk-pixbuf-2.0/loaders
)

for ldir in "${LOADER_DIRS[@]}"; do
    if [ -d "$ldir" ]; then
        echo "Found GdkPixbuf loader directory at $ldir"
        cp -d "$ldir"/*.so "$APP_DIR/usr/lib/gdk-pixbuf-2.0/loaders/" 2>/dev/null || true
    fi
done

# Explicit search for SVG loader if not already copied
if [ ! -f "$APP_DIR/usr/lib/gdk-pixbuf-2.0/loaders/libpixbufloader-svg.so" ]; then
    SVG_LOADER=$(find /usr/lib /usr/lib64 /lib /usr/lib/x86_64-linux-gnu -name "libpixbufloader-svg.so" 2>/dev/null | head -n 1)
    if [ -n "$SVG_LOADER" ] && [ -f "$SVG_LOADER" ]; then
        echo "Found SVG loader at $SVG_LOADER"
        cp -d "$SVG_LOADER" "$APP_DIR/usr/lib/gdk-pixbuf-2.0/loaders/" 2>/dev/null || true
    fi
fi

# Generate loaders.cache
QUERY_LOADERS=""
for qtool in "gdk-pixbuf-query-loaders" \
             "/usr/lib/x86_64-linux-gnu/gdk-pixbuf-2.0/gdk-pixbuf-query-loaders" \
             "/usr/lib/gdk-pixbuf-2.0/gdk-pixbuf-query-loaders" \
             "/usr/lib64/gdk-pixbuf-2.0/gdk-pixbuf-query-loaders"; do
    if command -v "$qtool" >/dev/null 2>&1 || [ -x "$qtool" ]; then
        QUERY_LOADERS="$qtool"
        break
    fi
done

CACHE_FILE="$APP_DIR/usr/lib/gdk-pixbuf-2.0/loaders.cache"
if [ -n "$QUERY_LOADERS" ]; then
    echo "Generating loaders.cache using $QUERY_LOADERS..."
    if ls "$APP_DIR/usr/lib/gdk-pixbuf-2.0/loaders"/*.so >/dev/null 2>&1; then
        "$QUERY_LOADERS" "$APP_DIR/usr/lib/gdk-pixbuf-2.0/loaders"/*.so > "$CACHE_FILE" 2>/dev/null || true
    else
        "$QUERY_LOADERS" > "$CACHE_FILE" 2>/dev/null || true
    fi
    # Make loader paths relative to GDK_PIXBUF_MODULEDIR for runtime portability
    sed -i -E 's#"/.*/loaders/#"#' "$CACHE_FILE" 2>/dev/null || true
fi

# Fallback: copy system loaders.cache if generated cache is empty
if [ ! -s "$CACHE_FILE" ]; then
    for sys_cache in /usr/lib/x86_64-linux-gnu/gdk-pixbuf-2.0/*/loaders.cache \
                     /usr/lib/gdk-pixbuf-2.0/*/loaders.cache \
                     /usr/lib64/gdk-pixbuf-2.0/*/loaders.cache \
                     /usr/lib/gdk-pixbuf-2.0/loaders.cache; do
        if [ -f "$sys_cache" ]; then
            echo "Copying fallback system loaders.cache from $sys_cache..."
            cp "$sys_cache" "$CACHE_FILE"
            sed -i -E 's#"/.*/loaders/#"#' "$CACHE_FILE" 2>/dev/null || true
            break
        fi
    done
fi

echo "Resolving dynamic dependencies with ldd..."
EXCLUDE_REGEX="^(linux-vdso|libc\.so|libm\.so|libpthread\.so|libdl\.so|librt\.so|libresolv\.so|libnsl\.so|libutil\.so|ld-linux|libgcc_s\.so|libstdc\+\+\.so|libGL\.so|libGLX\.so|libEGL\.so|libGLES|libglapi\.so|libdrm\.so|libasound\.so)"

MAX_PASSES=5
for pass in $(seq 1 $MAX_PASSES); do
    NEW_LIBS_COPIED=0
    SO_FILES=$(find "$APP_DIR/usr/lib" "$APP_DIR/usr/bin" -type f \( -name "*.so" -o -name "*.so.*" -o -name "python3" \) 2>/dev/null)
    for so in $SO_FILES; do
        if [ ! -f "$so" ]; then
            continue
        fi
        DEPS=$(ldd "$so" 2>/dev/null | awk '/=> \// {print $3}' || true)
        for dep in $DEPS; do
            if [ ! -f "$dep" ]; then
                continue
            fi
            dep_name=$(basename "$dep")
            if echo "$dep_name" | grep -Eq "$EXCLUDE_REGEX"; then
                continue
            fi
            if [ ! -e "$APP_DIR/usr/lib/$dep_name" ]; then
                if [ -L "$dep" ]; then
                    real_target=$(readlink -f "$dep" 2>/dev/null || true)
                    if [ -f "$real_target" ]; then
                        cp -d "$real_target" "$APP_DIR/usr/lib/" 2>/dev/null || true
                    fi
                fi
                cp -d "$dep" "$APP_DIR/usr/lib/" 2>/dev/null || true
                NEW_LIBS_COPIED=1
            fi
        done
    done
    if [ "$NEW_LIBS_COPIED" -eq 0 ]; then
        echo "All dynamic dependencies resolved in pass $pass."
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
export LD_LIBRARY_PATH="$HERE/usr/lib:$HERE/usr/lib/x86_64-linux-gnu:$HERE/usr/lib64:${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

# GObject Introspection typelib path
export GI_TYPELIB_PATH="$HERE/usr/lib/girepository-1.0:$HERE/usr/lib/x86_64-linux-gnu/girepository-1.0:$HERE/usr/lib64/girepository-1.0:${GI_TYPELIB_PATH:+:$GI_TYPELIB_PATH}"

# Complete Python runtime isolation
export PYTHONHOME="$HERE/usr"
export PYTHONPATH="$HERE/usr/share/pardus-boot-analyzer:$HERE/usr/lib/python3/dist-packages:$HERE/usr/lib/python3/site-packages"
for sdir in "$HERE"/usr/lib/python*/site-packages "$HERE"/usr/lib/python*/dist-packages; do
    if [ -d "$sdir" ]; then
        PYTHONPATH="$PYTHONPATH:$sdir"
    fi
done
export PYTHONPATH

# GdkPixbuf loaders and cache
export GDK_PIXBUF_MODULEDIR="$HERE/usr/lib/gdk-pixbuf-2.0/loaders"
export GDK_PIXBUF_MODULE_FILE="$HERE/usr/lib/gdk-pixbuf-2.0/loaders.cache"

# GSettings schemas path
if [ -d "$HERE/usr/share/glib-2.0/schemas" ]; then
    export GSETTINGS_SCHEMA_DIR="$HERE/usr/share/glib-2.0/schemas:${GSETTINGS_SCHEMA_DIR:+:$GSETTINGS_SCHEMA_DIR}"
fi

# GTK3 modules path
if [ -d "$HERE/usr/lib/gtk-3.0" ]; then
    export GTK_PATH="$HERE/usr/lib/gtk-3.0:${GTK_PATH:+:$GTK_PATH}"
fi

# XDG data directories for icons and themes
export XDG_DATA_DIRS="$HERE/usr/share:${XDG_DATA_DIRS:-/usr/local/share:/usr/share}"

# Execute application using isolated AppDir python3
exec "$HERE/usr/bin/python3" "$HERE/usr/share/pardus-boot-analyzer/main.py" "$@"
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
rm -f "$OUTPUT_IMAGE"
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
