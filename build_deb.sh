#!/bin/bash
# Debian Packaging Script for Pardus Boot Analyzer
# Builds a standard Debian package (.deb) using native ar and tar,
# allowing compilation on non-Debian distributions (e.g. Arch, Fedora).

set -e

# Package variables
PKG_NAME="pardus-boot-analyzer"
PKG_VERSION="1.0.0"
BUILD_DIR="build_pkg"

echo "Creating clean build directories..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/share/$PKG_NAME"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/share/pixmaps"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/scalable/apps"

echo "Copying application files..."
cp -r main.py "$BUILD_DIR/usr/share/$PKG_NAME/"
cp -r src "$BUILD_DIR/usr/share/$PKG_NAME/"
cp -r ui "$BUILD_DIR/usr/share/$PKG_NAME/"
cp -r locale "$BUILD_DIR/usr/share/$PKG_NAME/"
cp pardus-boot-analyzer.svg "$BUILD_DIR/usr/share/$PKG_NAME/"
cp pardus-boot-analyzer.svg "$BUILD_DIR/usr/share/pixmaps/"
cp pardus-boot-analyzer.svg "$BUILD_DIR/usr/share/icons/hicolor/scalable/apps/"

# Remove pycache if any
find "$BUILD_DIR" -type d -name "__pycache__" -exec rm -rf {} + || true

echo "Creating launcher wrapper script..."
cat << 'EOF' > "$BUILD_DIR/usr/bin/$PKG_NAME"
#!/bin/bash
cd /usr/share/pardus-boot-analyzer
exec python3 main.py "$@"
EOF
chmod +x "$BUILD_DIR/usr/bin/$PKG_NAME"

echo "Creating desktop entry..."
cat << EOF > "$BUILD_DIR/usr/share/applications/$PKG_NAME.desktop"
[Desktop Entry]
Name=Pardus Başlangıç Yöneticisi
Comment=Sistem açılış süresini analiz et ve başlangıç programlarını yönet
Exec=$PKG_NAME
Icon=pardus-boot-analyzer
Terminal=false
Type=Application
Categories=System;Settings;GTK;
StartupNotify=true
EOF

echo "Creating debian control file..."
cat << EOF > "$BUILD_DIR/DEBIAN/control"
Package: $PKG_NAME
Version: $PKG_VERSION
Section: utils
Priority: optional
Architecture: all
Depends: python3, python3-gi, gir1.2-gtk-3.0, python3-cairo
Maintainer: İbrahim Hakkı Ergin <ibrahimh.ergin@gmail.com>
Description: Pardus Boot Analyzer and Optimizer
 A system tool to analyze boot times, manage autostart programs, and optimize systemd services for faster boot.
EOF

echo "Building manual debian package components..."
echo "2.0" > debian-binary

# Create control.tar.gz (ensuring root ownership for packaging standards)
cd "$BUILD_DIR/DEBIAN"
tar --owner=0 --group=0 -czf ../../control.tar.gz control
cd ../..

# Create data.tar.gz (ensuring root ownership for packaging standards)
cd "$BUILD_DIR"
tar --owner=0 --group=0 -czf ../data.tar.gz usr
cd ..

echo "Creating final .deb package using ar..."
ar rcs "${PKG_NAME}_${PKG_VERSION}_all.deb" debian-binary control.tar.gz data.tar.gz

echo "Cleaning up temporary files..."
rm -rf "$BUILD_DIR" debian-binary control.tar.gz data.tar.gz

echo "===================================================="
echo "Debian package successfully built:"
echo "-> ${PKG_NAME}_${PKG_VERSION}_all.deb"
echo ""
echo "You can install it on any Debian/Pardus system using:"
echo "   sudo dpkg -i ${PKG_NAME}_${PKG_VERSION}_all.deb"
echo "===================================================="
