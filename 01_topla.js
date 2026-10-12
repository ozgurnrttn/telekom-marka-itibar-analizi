// Google News RSS'ten aylık başlık toplama.
// Kullanım: tarayıcıda https://news.google.com/rss/search?q=Turkcell&hl=tr&gl=TR&ceid=TR:tr adresini açın,
// geliştirici konsoluna bu kodu yapıştırın. Bittiğinde haberler.tsv indirilir.
(async () => {
  const brands = { turkcell: 'Turkcell', turk_telekom: '"Türk Telekom"', vodafone: 'Vodafone' };
  const months = [];
  for (let y = 2023, m = 10; !(y === 2025 && m === 10);) {
    const a = `${y}-${String(m).padStart(2, '0')}`;
    if (++m === 13) { m = 1; y++; }
    months.push([a, `${y}-${String(m).padStart(2, '0')}`]);
  }
  const dec = s => s.replace(/<!\[CDATA\[|\]\]>/g, '').replace(/&amp;/g, '&').replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'").replace(/&lt;/g, '<').replace(/&gt;/g, '>');
  const rows = [];
  for (const [b, q] of Object.entries(brands)) {
    for (const [a, n] of months) {
      const u = `/rss/search?q=${encodeURIComponent(`${q} after:${a}-01 before:${n}-01`)}&hl=tr&gl=TR&ceid=TR:tr`;
      const x = await (await fetch(u)).text();
      for (const it of x.split('<item>').slice(1)) {
        const g = t => { const mm = it.match(new RegExp(`<${t}[^>]*>([\\s\\S]*?)</${t}>`)); return mm ? dec(mm[1]) : ''; };
        const src = g('source');
        const dom = ((it.match(/<source url="([^"]*)"/) || [])[1] || '').replace(/^https?:\/\//, '').replace(/\/.*$/, '');
        let t = g('title');
        if (src && t.endsWith(' - ' + src)) t = t.slice(0, -(src.length + 3));
        rows.push([b, a, new Date(g('pubDate')).toISOString().slice(0, 10), src, dom, t]);
      }
      await new Promise(r => setTimeout(r, 700));
    }
  }
  const tsv = 'marka\tay\ttarih\tkaynak\talan\tbaslik\n' + rows.map(r => r.map(s => String(s).replace(/[\t\n\r]/g, ' ')).join('\t')).join('\n') + '\n';
  const el = document.createElementNS('http://www.w3.org/1999/xhtml', 'a');
  el.href = URL.createObjectURL(new Blob(['﻿' + tsv], { type: 'text/plain;charset=utf-8' }));
  el.download = 'haberler.tsv';
  document.documentElement.appendChild(el); el.click();
  console.log(rows.length, 'başlık');
})();
