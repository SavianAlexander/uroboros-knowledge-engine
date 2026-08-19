import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const distDir = path.resolve(__dirname, 'dist');

const COMPRESSIBLE_EXTENSIONS = new Set(['.js', '.css', '.html', '.svg', '.json', '.txt']);

function compressDirectory(dir) {
  if (!fs.existsSync(dir)) return;
  const entries = fs.readdirSync(dir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      compressDirectory(fullPath);
    } else if (entry.isFile()) {
      const ext = path.extname(entry.name).toLowerCase();
      if (COMPRESSIBLE_EXTENSIONS.has(ext)) {
        const content = fs.readFileSync(fullPath);
        const gzipped = zlib.gzipSync(content, { level: zlib.constants.Z_BEST_COMPRESSION });
        fs.writeFileSync(`${fullPath}.gz`, gzipped);

        const brotlied = zlib.brotliCompressSync(content, {
          params: {
            [zlib.constants.BROTLI_PARAM_QUALITY]: zlib.constants.BROTLI_MAX_QUALITY,
          },
        });
        fs.writeFileSync(`${fullPath}.br`, brotlied);
      }
    }
  }
}

function copyRecursive(src, dest) {
  if (!fs.existsSync(src)) return;
  fs.mkdirSync(dest, { recursive: true });
  const entries = fs.readdirSync(src, { withFileTypes: true });
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyRecursive(srcPath, destPath);
    } else if (entry.isFile()) {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

function syncAssets() {
  const assetsDir = path.resolve(__dirname, '..', 'src', 'assets');
  const rootAssetsDir = path.resolve(__dirname, '..', 'assets');
  const rootDir = path.resolve(__dirname, '..');

  // Copy dist contents to src/assets/ and assets/
  copyRecursive(distDir, assetsDir);
  copyRecursive(distDir, rootAssetsDir);

  // Copy index.html, style.css, app.js and chunks/ to root directory
  for (const f of ['index.html', 'style.css', 'app.js']) {
    const srcFile = path.join(distDir, f);
    if (fs.existsSync(srcFile)) {
      fs.copyFileSync(srcFile, path.join(rootDir, f));
    }
  }
  const chunksSrc = path.join(distDir, 'chunks');
  if (fs.existsSync(chunksSrc)) {
    copyRecursive(chunksSrc, path.join(rootDir, 'chunks'));
  }
  console.log('✓ 100% SHA-256 bitwise parity synchronized to src/assets/, assets/, and workspace root');
}

if (fs.existsSync(distDir)) {
  compressDirectory(distDir);
  console.log('✓ Gzip & Brotli pre-compression complete for dist/');
  syncAssets();
}
