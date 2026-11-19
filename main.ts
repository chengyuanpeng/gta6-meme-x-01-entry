import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const botDir = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

try {
  mkdirSync(outputDir, { recursive: true });
  copyFileSync(join(botDir, 'POST.json'), join(outputDir, 'POST.json'));
} catch (error) {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`Could not copy POST.json from ${botDir}: ${message}`);
  process.exitCode = 1;
}
