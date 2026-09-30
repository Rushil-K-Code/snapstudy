"""Compile + profile the ASR model on a Snapdragon X Elite via Qualcomm AI Hub.

Needs a free AI Hub account/API token (`qai-hub configure --api_token ...`).
Run:  python qualcomm_npu.py
It prints the AI Hub job URLs and writes profile.json. NOTE: numbers only exist after
you run this yourself; none are hard-coded in this repo.
"""
import json, sys

def main():
    try:
        import qai_hub as hub
        from qai_hub_models.models.whisper_base_en import Model
    except ImportError:
        sys.exit("pip install qai-hub qai-hub-models[whisper-base-en]  then  qai-hub configure --api_token <TOKEN>")
    device = hub.get_devices(name="Snapdragon X Elite CRD")[0]
    model = Model.from_pretrained()
    enc = model.encoder.convert_to_torchscript() if hasattr(model, "encoder") else None
    if enc is None:
        sys.exit("Model layout changed; see https://aihub.qualcomm.com for current export steps.")
    specs = model.encoder.sample_inputs()
    compile_job = hub.submit_compile_job(model=enc, device=device,
                                         input_specs={k: (v[0].shape, str(v[0].dtype)) for k, v in specs.items()})
    compile_job.wait()
    profile_job = hub.submit_profile_job(model=compile_job.get_target_model(), device=device,
                                         inputs=specs)
    profile_job.wait()
    p = profile_job.download_profile()
    out = {"device": device.name,
           "inference_ms": p["execution_summary"]["estimated_inference_time"] / 1000,
           "peak_mem_mb": p["execution_summary"]["inference_memory_peak_range_mb"]}
    json.dump(out, open("profile.json", "w"), indent=2)
    print(out, "\nCompile:", compile_job.url, "\nProfile:", profile_job.url)

if __name__ == "__main__":
    main()
