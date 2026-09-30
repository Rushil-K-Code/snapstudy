# SnapStudy: an offline lecture companion for Snapdragon AI PCs

**Snapdragon AI Lab Build & Present Challenge 2026 - individual submission**

SnapStudy turns a lecture transcript (or audio) into a **summary, flashcards and a study report**, entirely on the
student's own laptop. No account, no cloud, no data leaves the device.

## Problem
Students on campuses with weak Wi-Fi, or paying per-GB for mobile data, cannot use cloud AI note tools, and many
should not upload lectures or personal notes to servers abroad. On-device AI is the only option that reaches them.

## Why Snapdragon
Lecture processing runs for long stretches in the background. The Hexagon NPU gives high AI throughput at low power,
so a laptop can transcribe and summarise a class without draining the battery or spinning up fans. Running on-device
also gives privacy by design.

## What works today (verified)
- End-to-end pipeline: transcript -> extractive summary -> definition and cloze flashcards -> Markdown report.
- **Zero third-party dependencies** for the core engine (Python 3.9+ stdlib), so anyone can run it in seconds.
- Local web UI (`--serve`), bound to 127.0.0.1 only.
- Automatic runtime selection through ONNX Runtime: **QNN (Hexagon NPU) > DirectML > CPU**.
- Unit tests in `tests/`.

## Honest scope
- **I do not own a Snapdragon laptop.** All results here were run on a standard CPU. **No NPU latency or power
  figures are claimed.**
- The NPU path is implemented as a deployment route: `qualcomm_npu.py` (Qualcomm AI Hub compile + profile of
  Whisper-Base-En) and the QNN provider selection in `snapstudy.py`. `qualcomm_npu.py` has **not yet been run
  against AI Hub** and may need small API adjustments.
- Summaries and flashcards use a deterministic extractive engine, not a generative LLM. A local LLM (for example
  Llama-3.2-3B from Qualcomm AI Hub) is the planned upgrade through the same pipeline.

## Run it
```bash
python snapstudy.py samples/lecture.txt -o report.md     # CLI
python snapstudy.py --serve                               # local UI at http://127.0.0.1:8765
python snapstudy.py lecture.mp3                           # audio, needs: pip install faster-whisper
python tests/test_core.py
```
Sample output: `samples/report.md`. Snapdragon setup: `run_on_snapdragon.md`.

## Architecture
```
audio/.txt -> [Whisper ASR, local] -> transcript -> [TF-IDF extractive summary] -> summary
                                                  -> [definition + cloze generator] -> flashcards
                                                  -> Markdown report (local file)
ONNX Runtime provider: QNN (Hexagon NPU) | DirectML | CPU
```

## Mapping to the judging criteria
| Criterion | How SnapStudy addresses it |
|---|---|
| Technical Implementation | Working pipeline, tests, provider auto-selection, AI Hub compile/profile script |
| Use Case & Innovation | Offline study tool for low-connectivity, cost-sensitive students |
| Deployment & Accessibility | No internet, no GPU, no cost, no account; stdlib-only core |
| Presentation & Documentation | This README, sample report, pitch deck, Snapdragon run guide |

## Roadmap
1. Measure Whisper on a real Snapdragon X device and publish latency and memory.
2. Swap in a local LLM via Qualcomm AI Hub / GenieX for abstractive summaries.
3. Add multilingual (Hindi, English) transcription.

License: MIT
