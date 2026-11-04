import { readFile, writeFile } from 'node:fs/promises';

const root = new URL('.', import.meta.url);
const [htmlSource, css, engineSource, appSource] = await Promise.all([
  readFile(new URL('index.html', root), 'utf8'),
  readFile(new URL('styles.css', root), 'utf8'),
  readFile(new URL('game-engine.mjs', root), 'utf8'),
  readFile(new URL('app.mjs', root), 'utf8'),
]);

const engine = engineSource.replace(/^export\s+/gm, '');
const app = appSource.replace(/^import\s+.*?;\s*/s, '');

let html = htmlSource
  .replace('<link rel="stylesheet" href="styles.css">', `<style>\n${css}\n</style>`)
  .replace('<script type="module" src="app.mjs"></script>', '');

html = html.replace(
  '</body>',
  `<script>\n${engine}\n\n${app}\n</script>\n</body>`,
);

if (/<(?:script|link)[^>]+(?:src|href)="(?:styles\.css|app\.mjs|game-engine\.mjs)"/i.test(html)) {
  throw new Error('Standalone build still references a project asset.');
}

await writeFile(new URL('memory-reboot.html', root), html);
console.log('Built memory-reboot.html (self-contained, no external runtime assets).');
