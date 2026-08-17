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

if (fs.existsSync(distDir)) {
  compressDirectory(distDir);
  console.log('✓ Gzip & Brotli pre-compression complete for dist/');
}
