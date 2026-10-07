"""Finder’dan çift tıklanınca sunucuyu arka planda açıp hazır ekranı göster."""
import fcntl
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
URL = "http://127.0.0.1:7868"
os.environ.setdefault('HF_HUB_DISABLE_TELEMETRY', '1')


def ensure_models():
    from huggingface_hub import hf_hub_download
    from huggingface_hub.errors import LocalEntryNotFoundError
    for name in ('config.json', 'ema.pt', 'decoder.pt'):
        try:
            hf_hub_download('canberkkkkkk/ema-lightning', name, local_files_only=True)
        except LocalEntryNotFoundError:
            print(f'Model dosyası indiriliyor: {name}', flush=True)
            hf_hub_download('canberkkkkkk/ema-lightning', name)


def ready():
    try:
        with urllib.request.urlopen(URL + "/health", timeout=1) as response:
            return json.load(response).get("app") == "ema-lightning-local-v2"
    except (OSError, ValueError, urllib.error.URLError):
        return False


def main():
    # Çift tıklama ve ikinci açılış aynı sunucuyu kullanır.
    with (ROOT / ".launch.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if not ready():
            ensure_models()
            env = dict(os.environ, HF_HUB_OFFLINE="1", HF_HUB_DISABLE_TELEMETRY="1")
            with (ROOT / "uygulama.log").open("a") as log:
                process = subprocess.Popen([str(ROOT / ".venv/bin/python"), "-u", str(ROOT / "app.py")],
                                           cwd=ROOT, env=env, stdout=log, stderr=log,
                                           stdin=subprocess.DEVNULL, start_new_session=True)
            for _ in range(180):
                if ready():
                    break
                if process.poll() is not None:
                    raise RuntimeError("EMA açılamadı; uygulama.log dosyasını kontrol et.")
                time.sleep(0.5)
            else:
                process.terminate()
                raise RuntimeError("EMA hazırlığı tamamlanamadı; uygulama.log dosyasını kontrol et.")
    if "--no-browser" not in sys.argv:
        webbrowser.open(URL)
    print("EMA Ses hazır: " + URL)


if __name__ == "__main__":
    main()
