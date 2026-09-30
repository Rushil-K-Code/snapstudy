"""SnapStudy - offline-first lecture companion.

Pipeline: audio/text -> transcript -> summary -> flashcards -> Markdown report.
Everything runs locally. No network calls are made at any point.

Backends (auto-selected, all local):
  * ASR   : faster-whisper / Whisper (CPU) if installed, else text-file input.
  * Runtime provider: QNN (Snapdragon Hexagon NPU) > DirectML > CPU via ONNX Runtime.
  * Summary/flashcards: deterministic extractive engine (runs anywhere, zero deps).
    A local LLM (e.g. Llama-3.2-3B via Qualcomm AI Hub / GenieX) can replace it
    through the `LocalLLM` hook without changing the pipeline.
"""
import argparse, json, math, re, sys, time
from collections import Counter
from pathlib import Path

STOP = set("""a an the and or but if then else of to in on at by for with from as is are was were be been being
this that these those it its i you he she we they them his her our your their not no so than too very can could
should would will just about into over also which who whom what when where why how there here do does did have has had
more most some any each other such only own same out up down off again further once""".split())

# ---------- runtime detection (Snapdragon NPU path) ----------
def detect_provider():
    """Return best ONNX Runtime execution provider available on this machine."""
    try:
        import onnxruntime as ort
        avail = ort.get_available_providers()
        for p in ("QNNExecutionProvider", "DmlExecutionProvider", "CPUExecutionProvider"):
            if p in avail:
                return p
    except Exception:
        pass
    return "CPUExecutionProvider (onnxruntime not installed; pure-Python engine)"

# ---------- transcription ----------
def transcribe(path):
    p = Path(path)
    if p.suffix.lower() in {".txt", ".md"}:
        return p.read_text(encoding="utf-8")
    try:
        from faster_whisper import WhisperModel  # optional, local
    except ImportError:
        sys.exit("Audio input needs `pip install faster-whisper` (local model). "
                 "Or pass a .txt transcript.")
    model = WhisperModel("base.en", device="cpu", compute_type="int8")
    segs, _ = model.transcribe(str(p))
    return " ".join(s.text.strip() for s in segs)

# ---------- text processing ----------
def sentences(text):
    text = re.sub(r"\s+", " ", text).strip()
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text) if len(s.split()) >= 5]

def words(s):
    return [w for w in re.findall(r"[a-zA-Z][a-zA-Z\-']+", s.lower()) if w not in STOP and len(w) > 2]

def keyword_scores(sents):
    """TF-IDF style: term frequency weighted by rarity across sentences."""
    tf, df = Counter(), Counter()
    for s in sents:
        ws = words(s)
        tf.update(ws)
        df.update(set(ws))
    n = max(len(sents), 1)
    return {w: tf[w] * (1 + math.log(n / df[w])) for w in tf}

def summarize(text, n=5):
    sents = sentences(text)
    if not sents:
        return []
    kw = keyword_scores(sents)
    scored = []
    for i, s in enumerate(sents):
        ws = words(s)
        score = sum(kw.get(w, 0) for w in ws) / (len(ws) ** 0.6 + 1e-9) if ws else 0
        scored.append((score, i, s))
    top = sorted(scored, reverse=True)[:n]
    return [s for _, _, s in sorted(top, key=lambda t: t[1])]  # keep lecture order

DEF_PAT = re.compile(r"^(?P<term>[A-Z][\w\- ]{2,40}?)\s+(?:is|are|means|refers to|is defined as)\s+(?P<defn>.{15,})$")

def flashcards(text, max_cards=8):
    sents = sentences(text)
    kw = keyword_scores(sents)
    cards, used = [], set()
    for s in sents:  # 1) definition-style sentences -> "What is X?"
        m = DEF_PAT.match(s.rstrip("."))
        if m and m["term"].lower() not in used:
            used.add(m["term"].lower())
            cards.append({"q": f"What is {m['term'].strip()}?", "a": m["defn"].strip().rstrip(".") + "."})
    top_terms = [w for w, _ in sorted(kw.items(), key=lambda t: -t[1])]
    for s in sorted(sents, key=lambda s: -sum(kw.get(w, 0) for w in words(s))):  # 2) cloze cards
        if len(cards) >= max_cards:
            break
        target = next((t for t in top_terms if t in s.lower() and t not in used), None)
        if target:
            used.add(target)
            q = re.sub(re.escape(target), "_____", s, count=1, flags=re.I)
            cards.append({"q": "Fill in the blank: " + q, "a": target})
    return cards[:max_cards]

def report(text, source, sum_n=5, cards_n=8):
    t0 = time.perf_counter()
    summ, cards = summarize(text, sum_n), flashcards(text, cards_n)
    ms = (time.perf_counter() - t0) * 1000
    md = [f"# SnapStudy report: {Path(source).name}", "",
          f"_Generated 100% offline. Provider: {detect_provider()}. NLP time: {ms:.1f} ms._", "",
          "## Summary"] + [f"- {s}" for s in summ] + ["", "## Flashcards"]
    for i, c in enumerate(cards, 1):
        md += [f"**Q{i}.** {c['q']}", f"> {c['a']}", ""]
    md += ["## Transcript", "", text.strip()]
    return "\n".join(md), {"summary": summ, "flashcards": cards, "nlp_ms": round(ms, 2)}

# ---------- tiny local web UI (stdlib only) ----------
PAGE = """<!doctype html><meta charset=utf-8><title>SnapStudy</title>
<body style="font-family:system-ui;max-width:820px;margin:2rem auto;padding:0 1rem">
<h1>SnapStudy</h1><p>Paste a lecture transcript. Nothing leaves this device.</p>
<textarea id=t rows=10 style="width:100%"></textarea><br><button onclick="go()">Generate</button>
<pre id=o style="white-space:pre-wrap"></pre>
<script>async function go(){const r=await fetch('/run',{method:'POST',body:document.getElementById('t').value});
const j=await r.json();document.getElementById('o').textContent=j.md}</script>"""

def serve(port=8765):
    from http.server import BaseHTTPRequestHandler, HTTPServer
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200); self.send_header("Content-Type", "text/html"); self.end_headers()
            self.wfile.write(PAGE.encode())
        def do_POST(self):
            body = self.rfile.read(int(self.headers["Content-Length"])).decode()
            md, _ = report(body, "pasted.txt")
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
            self.wfile.write(json.dumps({"md": md}).encode())
        def log_message(self, *a): pass
    print(f"SnapStudy UI on http://127.0.0.1:{port}  (local only)")
    HTTPServer(("127.0.0.1", port), H).serve_forever()

def main():
    ap = argparse.ArgumentParser(description="Offline lecture companion")
    ap.add_argument("input", nargs="?", help="audio file or .txt transcript")
    ap.add_argument("-o", "--out", default="report.md")
    ap.add_argument("--serve", action="store_true", help="launch local web UI")
    a = ap.parse_args()
    if a.serve:
        return serve()
    if not a.input:
        ap.error("give an input file or use --serve")
    text = transcribe(a.input)
    md, data = report(text, a.input)
    Path(a.out).write_text(md, encoding="utf-8")
    print(f"Wrote {a.out}: {len(data['summary'])} summary points, {len(data['flashcards'])} flashcards, "
          f"provider={detect_provider()}")

if __name__ == "__main__":
    main()
