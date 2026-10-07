"""EMA: yerel ses üretimi, tonu koruyarak hız değişimi ve WAV indirme."""
import json
import os
import re
import secrets
import shutil
import subprocess
import threading
import time
import uuid
import wave
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
import torch
from ema_lightning import EMA

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "sesler"
URL = "http://127.0.0.1:7868"
TOKEN = secrets.token_urlsafe(32)
LOCK = threading.Lock()
SPEEDS = (0.75, 0.9, 1, 1.25, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7)
FFMPEG = shutil.which('ffmpeg') or next((str(path) for path in (Path('/opt/homebrew/bin/ffmpeg'), Path('/usr/local/bin/ffmpeg')) if path.is_file()), 'ffmpeg')


def speech_text(text):
    text = re.sub(r'!\[[^]]*\]\([^)]*\)', ' ', text)
    text = re.sub(r'\[([^]]+)\]\([^)]*\)', r'\1', text)
    text = re.sub(r'(?i)(?<![\w@])(?:https?://|www\.)[^\s)\]}>]+|(?<![\w@])(?:[a-z0-9-]+\.)+[a-z]{2,}(?:/[^\s)\]}>]*)?', ' ', text)
    text = re.sub(r'\(\s*\)|\[\s*\]|<\s*>', ' ', text)
    text = re.sub(r'(?m)^[ \t]*(?:[-+*]|#{1,6})[ \t]+', '', text)
    return text.translate(str.maketrans('', '', '*_`~#')).strip()


def audio_path(name):
    if not isinstance(name, str) or len(name) != 36 or not name.endswith(".wav") or any(c not in "0123456789abcdef" for c in name[:-4]):
        raise ValueError("Geçersiz ses dosyası.")
    path = OUTPUT / name
    if not path.is_file():
        raise ValueError("Ses bulunamadı. Metni yeniden üret.")
    return path


def check_speed(speed):
    if isinstance(speed, bool) or not isinstance(speed, (int, float)) or speed not in SPEEDS:
        raise ValueError("Listeden bir okuma hızı seç.")
    return speed


def tempo_filter(speed):
    factors = []
    while speed > 2:
        factors.append(2)
        speed /= 2
    factors.append(speed)
    return ",".join(f"atempo={factor:g}" for factor in factors)


def change_speed(source, speed):
    original = audio_path(source)
    target = original
    if speed != 1:
        target = OUTPUT / (uuid.uuid4().hex + ".wav")
        subprocess.run([FFMPEG, "-nostdin", "-v", "error", "-i", str(original),
                        "-af", tempo_filter(speed), "-ar", "48000", "-ac", "1", str(target)],
                       check=True, capture_output=True, timeout=180)
    with wave.open(str(target)) as wav:
        duration = wav.getnframes() / wav.getframerate()
    return {"url": "/sesler/" + target.name, "source": source, "duration": duration, "speed": speed}


class Handler(BaseHTTPRequestHandler):
    def send(self, code, data, content_type):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(data)

    def json(self, code, data):
        self.send(code, json.dumps(data, ensure_ascii=False).encode(), "application/json; charset=utf-8")

    def send_audio(self, path, download=False):
        data = path.read_bytes()
        total = len(data)
        start, end, code = 0, total - 1, 200
        requested = self.headers.get('Range')
        if requested:
            match = re.fullmatch(r'bytes=(\d*)-(\d*)', requested)
            if not match or not any(match.groups()):
                self.send_error(416)
                return
            left, right = match.groups()
            if left:
                start, end = int(left), min(int(right), total - 1) if right else total - 1
            else:
                start = max(0, total - int(right))
            if start > end or start >= total:
                self.send_response(416)
                self.send_header('Content-Range', f'bytes */{total}')
                self.send_header('Content-Length', '0')
                self.end_headers()
                return
            code = 206
        self.send_response(code)
        self.send_header('Content-Type', 'audio/wav')
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Length', str(end - start + 1))
        self.send_header('Cache-Control', 'no-store')
        if code == 206:
            self.send_header('Content-Range', f'bytes {start}-{end}/{total}')
        if download:
            self.send_header('Content-Disposition', 'attachment; filename="ema-ses.wav"')
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(data[start:end + 1])

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        if self.path == "/":
            self.send(200, (ROOT / "index.html").read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/health":
            self.json(200, {"app": "ema-lightning-local-v2", "ready": True})
        elif self.path == "/session":
            self.json(200, {"token": TOKEN})
        elif self.path.startswith(("/sesler/", "/download/")):
            try:
                path = audio_path(self.path.split('/')[-1])
                self.send_audio(path, download=self.path.startswith('/download/'))
            except ValueError:
                self.json(404, {"error": "Ses dosyası bulunamadı."})
        else:
            self.json(404, {"error": "Sayfa bulunamadı."})

    def do_POST(self):
        if self.path not in ("/say", "/tempo", "/stop"):
            self.json(404, {"error": "İşlem bulunamadı."})
            return
        if self.headers.get("X-EMA-Token") != TOKEN:
            self.json(403, {"error": "Bu ekran eski bir oturuma ait. Sayfayı yenileyip tekrar dene."})
            return
        if self.path == "/stop":
            self.json(200, {})
            threading.Thread(target=self.server.shutdown, daemon=True).start()
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 80000:
                raise ValueError("Metin çok uzun veya istek boş.")
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise ValueError("Geçersiz istek.")
            speed = check_speed(payload.get("speed", 1))
            start = time.perf_counter()
            if self.path == "/say":
                text = payload.get("text")
                if not isinstance(text, str) or len(text) > 10000:
                    raise ValueError("1–10.000 karakter arası bir metin yaz.")
                text = speech_text(text)
                if not text:
                    raise ValueError("1–10.000 karakter arası bir metin yaz.")
                source = uuid.uuid4().hex + ".wav"
                # ponytail: tek kullanıcı için sıralı üretim; çok kullanıcılı ihtiyaçta değişir.
                with LOCK:
                    self.server.tts.say(text, speed=1, path=str(OUTPUT / source))
            else:
                source = payload.get("source")
            data = change_speed(source, speed)
            data["elapsed"] = time.perf_counter() - start
            self.json(200, data)
        except (ValueError, TypeError) as error:
            self.json(400, {"error": str(error)})
        except Exception as error:
            print(f"Ses işlemi hatası: {error}", flush=True)
            self.json(500, {"error": "Ses işlenemedi. Uygulamayı kapatıp EMA Ses’i yeniden aç."})


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 7868), Handler)
    OUTPUT.mkdir(exist_ok=True)
    torch.set_num_threads(4)
    print("EMA hazırlanıyor…", flush=True)
    server.tts = EMA(device="cpu")
    # İlk üretimin hazırlık maliyetini ekran açılmadan tamamla.
    server.tts.say("Merhaba, Türkçe ses üretimi için her şey hazır.", seed=0)
    print(f"Hazır: {URL}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
