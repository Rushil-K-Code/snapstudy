# Running on a Snapdragon X HP PC (Windows 11 ARM64)
1. Install ARM64 Python 3.11+ and `pip install onnxruntime-qnn faster-whisper`.
2. `python snapstudy.py samples/lecture.txt` - the report header shows which provider was picked
   (QNNExecutionProvider = Hexagon NPU).
3. `python qualcomm_npu.py` to compile/profile Whisper on the NPU via AI Hub and record real latency.
