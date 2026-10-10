// Batch KaTeX renderer: reads JSON [{tex, display}] from stdin, writes JSON [html|{error}] to stdout.
const katex = require('katex');
let buf = '';
process.stdin.on('data', d => buf += d);
process.stdin.on('end', () => {
  const items = JSON.parse(buf);
  const macros = {
    "\\E": "\\mathbb{E}", "\\Var": "\\operatorname{Var}", "\\Cov": "\\operatorname{Cov}",
    "\\R": "\\mathbb{R}", "\\dd": "\\,\\mathrm{d}", "\\given": "\\,\\middle|\\,",
  };
  const out = items.map(it => {
    try {
      return katex.renderToString(it.tex, { displayMode: !!it.display, throwOnError: true,
        output: 'html', strict: 'ignore', trust: false, macros: {...macros} });
    } catch (e) { return { error: String(e.message || e) }; }
  });
  process.stdout.write(JSON.stringify(out));
});
