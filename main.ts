// The World in One Day — Friday 20 November 2026 (v4).
// Entry for make.fun news-image-20261120. The repository ships one
// finished front-page image, entry.png, drawn and typeset by gen.py
// from generated illustrations and the day's verified story file.
// This program only delivers that image to the harness output path:
// no network, no inputs, and every run writes the identical bytes.

import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const repoDir = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
copyFileSync(join(repoDir, "entry.png"), join(outDir, "entry.png"));
console.log("entry.png delivered");
