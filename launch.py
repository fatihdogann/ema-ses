"""Yerel sunucuyu başlat ve hazır olduğunda tarayıcıyı aç."""
import json
import os
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

from filelock import FileLock, Timeout

ROOT = Path(__file__).resolve().parent
URL = "http://127.0.0.1:7868"
LOG = ROOT / "uygulama.log"
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
            data = json.load(response)
            return isinstance(data, dict) and data.get("app") == "ema-lightning-local-v2" and data.get("ready") is True
    except (OSError, ValueError):
        return False


def main():
    # Çift tıklama ve ikinci açılış aynı sunucuyu kullanır.
    with FileLock(str(ROOT / ".launch.lock"), timeout=300):
        if not ready():
            ensure_models()
            env = dict(os.environ, HF_HUB_OFFLINE="1", HF_HUB_DISABLE_TELEMETRY="1")
            background = ({"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt"
                          else {"start_new_session": True})
            with LOG.open("a", encoding="utf-8") as log:
                process = subprocess.Popen([sys.executable, "-u", str(ROOT / "app.py")],
                                           cwd=ROOT, env=env, stdout=log, stderr=log,
                                           stdin=subprocess.DEVNULL, **background)
            for _ in range(180):
                if ready():
                    break
                if process.poll() is not None:
                    raise RuntimeError("EMA açılamadı; uygulama.log dosyasını kontrol et.")
                time.sleep(0.5)
            else:
                process.terminate()
                process.wait(timeout=10)
                raise RuntimeError("EMA hazırlığı tamamlanamadı; uygulama.log dosyasını kontrol et.")
    if "--no-browser" not in sys.argv and not webbrowser.open(URL):
        print("Tarayıcı açılamadı. Şu adresi elle aç:", URL)
    print("EMA Ses hazır: " + URL)


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, Timeout) as error:
        sys.exit(f"EMA Ses başlatılamadı: {error}")
