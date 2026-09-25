"""Tiny local playground for the assistant (Google AI Studio has no File Search tool in its UI).

    python playground.py            # then open http://127.0.0.1:8787

Serves one page that posts a question to /ask; the server answers with the same
KnowledgeStore.ask() used by `main.py --ask`, so the key never reaches the browser.
"""

from __future__ import annotations

import json
import logging
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from kbsync.config import Settings
from kbsync.store import KnowledgeStore

PROMPT_PATH = Path(__file__).parent / "prompts" / "system_prompt.txt"

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>OptiBot playground</title>
<script src="https://cdn.jsdelivr.net/npm/marked@12/marked.min.js"></script>
<style>
  :root{--bg:#0f1115;--card:#171a21;--line:#2a2f3a;--txt:#e6e8ee;--muted:#9aa3b2;--accent:#4f8cff}
  body{margin:0;background:var(--bg);color:var(--txt);font:15px/1.5 system-ui,Segoe UI,Roboto,sans-serif}
  header{display:flex;justify-content:space-between;align-items:center;padding:14px 22px;border-bottom:1px solid var(--line)}
  header h1{font-size:17px;margin:0} header small{color:var(--muted)}
  main{max-width:900px;margin:0 auto;padding:22px}
  .sys{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 16px;color:var(--muted);white-space:pre-wrap;font-size:13px}
  .msg{margin-top:18px;padding:14px 18px;border-radius:12px;border:1px solid var(--line)}
  .user{background:#1b2230} .bot{background:var(--card)}
  .role{font-size:12px;color:var(--muted);margin-bottom:6px;text-transform:uppercase;letter-spacing:.04em}
  .bot ul{padding-left:20px} .bot a{color:var(--accent)}
  .cites{margin-top:12px;padding-top:10px;border-top:1px dashed var(--line);font-size:13px}
  .cites .t{color:var(--muted);margin-bottom:4px}
  .cites li{margin:3px 0} .cites code{color:var(--muted)}
  form{display:flex;gap:10px;margin-top:22px}
  input{flex:1;padding:12px 14px;border-radius:10px;border:1px solid var(--line);background:var(--card);color:var(--txt);font-size:15px}
  button{padding:12px 18px;border-radius:10px;border:0;background:var(--accent);color:#fff;font-weight:600;cursor:pointer}
  .meta{color:var(--muted);font-size:12px;margin-top:6px}
</style></head><body>
<header><h1>OptiBot &mdash; support assistant playground</h1><small id="meta"></small></header>
<main>
  <div class="sys" id="sys"></div>
  <div id="log"></div>
  <form id="f"><input id="q" placeholder="Ask a question about OptiSigns…" autocomplete="off" value="How do I add a YouTube video?"><button>Run</button></form>
</main>
<script>
const $=s=>document.querySelector(s);
fetch('/meta').then(r=>r.json()).then(m=>{$('#meta').textContent=`model ${m.model} · File Search store ${m.store}`;$('#sys').textContent='System instructions\\n'+m.system_prompt;});
$('#f').onsubmit=async e=>{
  e.preventDefault(); const q=$('#q').value.trim(); if(!q) return;
  const log=$('#log');
  log.insertAdjacentHTML('beforeend',`<div class="msg user"><div class="role">User</div>${q.replace(/</g,'&lt;')}</div>`);
  const bot=document.createElement('div'); bot.className='msg bot'; bot.innerHTML='<div class="role">OptiBot</div><em>Searching the knowledge base…</em>'; log.appendChild(bot);
  const r=await fetch('/ask',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({q})});
  const d=await r.json();
  if(d.error){bot.innerHTML='<div class="role">OptiBot</div><span style="color:#ff7b7b">'+d.error+'</span>';return;}
  const cites=d.citations.map(c=>`<li>${c.title}${c.url?` &rarr; <a href="${c.url}" target="_blank">${c.url}</a>`:''}</li>`).join('');
  bot.innerHTML=`<div class="role">OptiBot</div>${marked.parse(d.text)}<div class="cites"><div class="t">Grounding sources (File Search retrieved_context)</div><ul>${cites}</ul></div><div class="meta">${d.model} · ${d.elapsed_ms} ms</div>`;
  $('#q').value='';
};
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    settings: Settings
    store: KnowledgeStore
    system_prompt: str

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/meta":
            meta = {"model": self.settings.gemini_model, "store": self.store.store_name, "system_prompt": self.system_prompt}
            self._send(200, json.dumps(meta).encode(), "application/json")
        else:
            self._send(200, PAGE.encode(), "text/html; charset=utf-8")

    def do_POST(self) -> None:  # noqa: N802
        import time

        length = int(self.headers.get("Content-Length", "0"))
        question = json.loads(self.rfile.read(length) or b"{}").get("q", "")
        started = time.monotonic()
        try:
            answer = self.store.ask(question, model=self.settings.gemini_model, system_prompt=self.system_prompt)
            payload = {
                "text": answer.text,
                "citations": [c.__dict__ for c in answer.citations],
                "model": self.settings.gemini_model,
                "elapsed_ms": int((time.monotonic() - started) * 1000),
            }
        except Exception as exc:  # noqa: BLE001
            payload = {"error": str(exc)}
        self._send(200, json.dumps(payload).encode(), "application/json")

    def log_message(self, fmt: str, *args: object) -> None:
        logging.getLogger("playground").info(fmt, *args)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S", stream=sys.stdout)
    settings = Settings.from_env()
    store = KnowledgeStore(settings.gemini_api_key, settings.store_display_name)
    store.ensure_store()
    Handler.settings, Handler.store, Handler.system_prompt = settings, store, PROMPT_PATH.read_text(encoding="utf-8")
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
    print(f"OptiBot playground on http://127.0.0.1:{port}  (Ctrl+C to stop)")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
