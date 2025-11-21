#!/usr/bin/env node

/**
 * AI 반편성 시스템 아이콘 생성 스크립트
 * SVG를 여러 크기의 PNG로 변환
 */

const sharp = require('sharp');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const SVG_FILE = path.join(__dirname, '../frontend/src/assets/logo.svg');
const ICON_DIR = path.join(__dirname, '../frontend/src-tauri/icons');
const ICONSET_DIR = path.join(ICON_DIR, 'icon.iconset');

// iconset 디렉토리 생성
if (!fs.existsSync(ICONSET_DIR)) {
  fs.mkdirSync(ICONSET_DIR, { recursive: true });
}

console.log('🎨 아이콘 생성 시작...');

// SVG 파일 읽기
const svgBuffer = fs.readFileSync(SVG_FILE);

// 생성할 아이콘 크기 정의
const sizes = [
  { size: 16, name: 'icon_16x16.png' },
  { size: 32, name: 'icon_16x16@2x.png' },
  { size: 32, name: 'icon_32x32.png' },
  { size: 64, name: 'icon_32x32@2x.png' },
  { size: 128, name: 'icon_128x128.png' },
  { size: 256, name: 'icon_128x128@2x.png' },
  { size: 256, name: 'icon_256x256.png' },
  { size: 512, name: 'icon_256x256@2x.png' },
  { size: 512, name: 'icon_512x512.png' },
  { size: 1024, name: 'icon_512x512@2x.png' },
];

// PNG 파일 생성
console.log('📐 PNG 파일 생성 중...');

Promise.all(
  sizes.map(({ size, name }) => {
    const outputPath = path.join(ICONSET_DIR, name);
    return sharp(svgBuffer)
      .resize(size, size)
      .png()
      .toFile(outputPath)
      .then(() => console.log(`  ✓ ${name} (${size}x${size})`));
  })
)
  .then(() => {
    console.log('✅ PNG 파일 생성 완료\n');

    // .icns 파일 생성 (macOS만)
    if (process.platform === 'darwin') {
      console.log('🔨 .icns 파일 생성 중...');
      try {
        execSync(`iconutil -c icns "${ICONSET_DIR}" -o "${ICON_DIR}/icon.icns"`, {
          stdio: 'inherit',
        });
        console.log('✅ icon.icns 생성 완료\n');
      } catch (error) {
        console.error('❌ .icns 파일 생성 실패:', error.message);
      }
    }

    // Tauri에서 사용할 추가 PNG 파일 복사
    console.log('📋 추가 아이콘 파일 복사 중...');
    fs.copyFileSync(
      path.join(ICONSET_DIR, 'icon_32x32.png'),
      path.join(ICON_DIR, '32x32.png')
    );
    fs.copyFileSync(
      path.join(ICONSET_DIR, 'icon_128x128.png'),
      path.join(ICON_DIR, '128x128.png')
    );
    fs.copyFileSync(
      path.join(ICONSET_DIR, 'icon_128x128@2x.png'),
      path.join(ICON_DIR, '128x128@2x.png')
    );
    fs.copyFileSync(
      path.join(ICONSET_DIR, 'icon_256x256.png'),
      path.join(ICON_DIR, 'icon.png')
    );
    console.log('✅ 추가 아이콘 파일 복사 완료\n');

    // iconset 디렉토리 정리
    console.log('🧹 임시 파일 정리 중...');
    fs.rmSync(ICONSET_DIR, { recursive: true, force: true });
    console.log('✅ 임시 파일 정리 완료\n');

    console.log('🎉 아이콘 생성 완료!\n');
    console.log('생성된 파일:');
    if (process.platform === 'darwin') {
      console.log(`  - ${path.relative(process.cwd(), path.join(ICON_DIR, 'icon.icns'))} (macOS Dock 아이콘)`);
    }
    console.log(`  - ${path.relative(process.cwd(), path.join(ICON_DIR, '32x32.png'))}`);
    console.log(`  - ${path.relative(process.cwd(), path.join(ICON_DIR, '128x128.png'))}`);
    console.log(`  - ${path.relative(process.cwd(), path.join(ICON_DIR, '128x128@2x.png'))}`);
    console.log(`  - ${path.relative(process.cwd(), path.join(ICON_DIR, 'icon.png'))}`);
    console.log('\n💡 앱을 다시 빌드하면 새 아이콘이 적용됩니다:');
    console.log('   cd frontend && npm run tauri:dev');
  })
  .catch((error) => {
    console.error('❌ 아이콘 생성 실패:', error);
    process.exit(1);
  });

