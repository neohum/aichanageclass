#!/bin/bash

# AI 반편성 시스템 아이콘 생성 스크립트
# macOS .icns 파일 생성

set -e

echo "🎨 아이콘 생성 시작..."

# 소스 SVG 파일
SVG_FILE="frontend/src/assets/logo.svg"
ICON_DIR="frontend/src-tauri/icons"
ICONSET_DIR="frontend/src-tauri/icons/icon.iconset"

# iconset 디렉토리 생성
mkdir -p "$ICONSET_DIR"

# SVG를 PNG로 변환하는 함수
convert_svg_to_png() {
    local size=$1
    local output=$2
    
    if command -v rsvg-convert &> /dev/null; then
        # rsvg-convert 사용 (brew install librsvg)
        rsvg-convert -w $size -h $size "$SVG_FILE" -o "$output"
    elif command -v convert &> /dev/null; then
        # ImageMagick 사용 (brew install imagemagick)
        convert -background none -resize ${size}x${size} "$SVG_FILE" "$output"
    elif command -v qlmanage &> /dev/null; then
        # macOS 기본 도구 사용 (품질이 낮을 수 있음)
        echo "⚠️  rsvg-convert 또는 ImageMagick이 설치되지 않았습니다."
        echo "더 나은 품질을 위해 다음 중 하나를 설치하세요:"
        echo "  brew install librsvg"
        echo "  brew install imagemagick"
        return 1
    else
        echo "❌ SVG 변환 도구를 찾을 수 없습니다."
        echo "다음 중 하나를 설치하세요:"
        echo "  brew install librsvg"
        echo "  brew install imagemagick"
        return 1
    fi
}

# macOS .icns 파일에 필요한 모든 크기 생성
echo "📐 PNG 파일 생성 중..."

convert_svg_to_png 16 "$ICONSET_DIR/icon_16x16.png"
convert_svg_to_png 32 "$ICONSET_DIR/icon_16x16@2x.png"
convert_svg_to_png 32 "$ICONSET_DIR/icon_32x32.png"
convert_svg_to_png 64 "$ICONSET_DIR/icon_32x32@2x.png"
convert_svg_to_png 128 "$ICONSET_DIR/icon_128x128.png"
convert_svg_to_png 256 "$ICONSET_DIR/icon_128x128@2x.png"
convert_svg_to_png 256 "$ICONSET_DIR/icon_256x256.png"
convert_svg_to_png 512 "$ICONSET_DIR/icon_256x256@2x.png"
convert_svg_to_png 512 "$ICONSET_DIR/icon_512x512.png"
convert_svg_to_png 1024 "$ICONSET_DIR/icon_512x512@2x.png"

echo "✅ PNG 파일 생성 완료"

# .icns 파일 생성
echo "🔨 .icns 파일 생성 중..."
iconutil -c icns "$ICONSET_DIR" -o "$ICON_DIR/icon.icns"

echo "✅ icon.icns 생성 완료"

# Tauri에서 사용할 추가 PNG 파일 복사
echo "📋 추가 아이콘 파일 복사 중..."
cp "$ICONSET_DIR/icon_32x32.png" "$ICON_DIR/32x32.png"
cp "$ICONSET_DIR/icon_128x128.png" "$ICON_DIR/128x128.png"
cp "$ICONSET_DIR/icon_128x128@2x.png" "$ICON_DIR/128x128@2x.png"
cp "$ICONSET_DIR/icon_256x256.png" "$ICON_DIR/icon.png"

echo "✅ 추가 아이콘 파일 복사 완료"

# iconset 디렉토리 정리
echo "🧹 임시 파일 정리 중..."
rm -rf "$ICONSET_DIR"

echo "🎉 아이콘 생성 완료!"
echo ""
echo "생성된 파일:"
echo "  - $ICON_DIR/icon.icns (macOS Dock 아이콘)"
echo "  - $ICON_DIR/32x32.png"
echo "  - $ICON_DIR/128x128.png"
echo "  - $ICON_DIR/128x128@2x.png"
echo "  - $ICON_DIR/icon.png"
echo ""
echo "💡 앱을 다시 빌드하면 새 아이콘이 적용됩니다:"
echo "   cd frontend && npm run tauri:dev"

