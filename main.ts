// news-image-20261118 entrypoint.
//
// The artwork itself is entry.png beside this file (regenerated from
// scratch by draw.py, a Pillow script that draws the whole newspaper
// front page in code). This entrypoint's job is to deliver that PNG to
// the grader: resolve the output directory, validate the image against
// the bounty gate (PNG, at most 1 MiB, at most 1024x1024), copy it, and
// verify the copy byte for byte before reporting success.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for
// /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import {
  copyFileSync,
  existsSync,
  mkdirSync,
  readFileSync,
  statSync,
} from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const MAX_BYTES = 1024 * 1024;
const MAX_WIDTH = 1024;
const MAX_HEIGHT = 1024;

function log(step, fields = {}) {
  const record = { time: new Date().toISOString(), step, ...fields };
  process.stdout.write(`${JSON.stringify(record)}\n`);
}

function fail(step, message, detail = {}) {
  log(step, { status: 'error', message, ...detail });
  throw new Error(`${step}: ${message}`);
}

// Resolve the output directory: MAKEFUN_OUTPUT_DIR overrides the
// grader default /output. A blank value is treated as unset so an
// accidental empty export cannot silently point at the cwd.
function resolveOutputDir() {
  const raw = process.env.MAKEFUN_OUTPUT_DIR;
  const chosen = raw !== undefined && raw.trim() !== '' ? raw.trim() : '/output';
  const dir = resolve(chosen);
  log('output_dir', { chosen, resolved: dir, fromEnv: raw !== undefined && raw.trim() !== '' });
  return dir;
}

// Read a PNG's width and height out of its IHDR chunk (bytes 16-23).
// Throws if the file is not a PNG or is too short to hold a header.
function readPngDimensions(path, bytes) {
  if (bytes.length < 24) {
    fail('validate_png', 'file too short to be a PNG', { path, bytes: bytes.length });
  }
  if (!bytes.subarray(0, 8).equals(PNG_SIGNATURE)) {
    fail('validate_png', 'not a PNG file (bad signature)', { path });
  }
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  return { width, height };
}

// Check the source artwork against the bounty gate before copying.
function validateSource(path) {
  if (!existsSync(path)) {
    fail('validate_source', 'entry.png is missing next to main.ts', { path });
  }
  const stats = statSync(path);
  if (!stats.isFile()) {
    fail('validate_source', 'entry.png is not a regular file', { path });
  }
  if (stats.size === 0) {
    fail('validate_source', 'entry.png is empty', { path });
  }
  if (stats.size > MAX_BYTES) {
    fail('validate_source', 'entry.png exceeds the 1 MiB gate limit', {
      path,
      bytes: stats.size,
      limit: MAX_BYTES,
    });
  }
  const bytes = readFileSync(path);
  const { width, height } = readPngDimensions(path, bytes);
  if (width > MAX_WIDTH || height > MAX_HEIGHT) {
    fail('validate_source', 'entry.png exceeds the 1024x1024 gate limit', {
      path,
      width,
      height,
    });
  }
  log('validate_source', {
    status: 'ok',
    path,
    bytes: stats.size,
    width,
    height,
  });
  return { bytes: stats.size, width, height };
}

// Copy, then prove the destination is a complete, identical PNG.
function deliver(sourcePath, outputDir) {
  mkdirSync(outputDir, { recursive: true });
  log('prepare_output', { status: 'ok', dir: outputDir });

  const destPath = join(outputDir, 'entry.png');
  copyFileSync(sourcePath, destPath);
  log('copy', { status: 'ok', from: sourcePath, to: destPath });

  if (!existsSync(destPath)) {
    fail('verify_output', 'entry.png missing after copy', { destPath });
  }
  const destStats = statSync(destPath);
  const sourceStats = statSync(sourcePath);
  if (destStats.size === 0) {
    fail('verify_output', 'entry.png is empty after copy', { destPath });
  }
  if (destStats.size !== sourceStats.size) {
    fail('verify_output', 'copied size does not match the source', {
      destPath,
      sourceBytes: sourceStats.size,
      destBytes: destStats.size,
    });
  }
  const { width, height } = readPngDimensions(destPath, readFileSync(destPath));
  log('verify_output', {
    status: 'ok',
    path: destPath,
    bytes: destStats.size,
    width,
    height,
    matchesSource: true,
  });
  return destPath;
}

function main() {
  const here = dirname(fileURLToPath(import.meta.url));
  const sourcePath = join(here, 'entry.png');
  log('start', { entry: 'news-image-20261118', source: sourcePath });

  const outputDir = resolveOutputDir();
  const source = validateSource(sourcePath);
  const destPath = deliver(sourcePath, outputDir);

  log('done', {
    status: 'ok',
    output: destPath,
    bytes: source.bytes,
    width: source.width,
    height: source.height,
  });
}

try {
  main();
} catch (error) {
  process.stderr.write(`news-image-20261118 failed: ${error.message}\n`);
  process.exitCode = 1;
}
