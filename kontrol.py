"""Çalışan yerel ekranın üretim, WAV ve giriş sınırlarını kontrol et."""
import io
import json
import urllib.error
import urllib.request
import wave

URL = "http://127.0.0.1:7868"
token = json.load(urllib.request.urlopen(URL + '/session'))['token']


def request(payload, token_value=token, route='/say'):
    req = urllib.request.Request(URL + route, json.dumps(payload).encode(),
                                 {"Content-Type": "application/json", "X-EMA-Token": token_value})
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, json.load(error)


for payload in ({"text": ""}, {"text": "a" * 10001}, {"text": "Merhaba.", "speed": True}, []):
    assert request(payload)[0] == 400
assert request({"text": "Merhaba."}, "yanlis")[0] == 403
code, result = request({"text": "Bugün hava oldukça güzel. Türkçe metinleri bilgisayarımızda kolayca seslendirebiliriz. Ürettiğimiz sesi doğrudan web sitesinde dinleyebilir, daha sonra bilgisayarımıza indirip yeniden kullanabiliriz.", "speed": 1})
assert code == 200, result
audio = urllib.request.urlopen(URL + result["url"]).read()
with wave.open(io.BytesIO(audio)) as wav:
    assert wav.getframerate() == 48000 and wav.getnchannels() == 1 and wav.getnframes() > 48000
for interval, expected in [('bytes=0-1', audio[:2]), ('bytes=-16', audio[-16:]), ('bytes=32-63', audio[32:64])]:
    req = urllib.request.Request(URL + result['url'], headers={'Range': interval})
    with urllib.request.urlopen(req) as response:
        assert response.status == 206 and response.read() == expected
        assert response.headers['Accept-Ranges'] == 'bytes'
req = urllib.request.Request(URL + result['url'], method='HEAD')
with urllib.request.urlopen(req) as response:
    assert int(response.headers['Content-Length']) == len(audio) and not response.read()
req = urllib.request.Request(URL + result['url'].replace('/sesler/', '/download/'))
with urllib.request.urlopen(req) as response:
    assert 'attachment' in response.headers['Content-Disposition'] and response.read() == audio
from app import SPEEDS
durations = {}
for speed in SPEEDS:
    code, changed = request({'source': result['source'], 'speed': speed}, route='/tempo')
    assert code == 200, changed
    audio = urllib.request.urlopen(URL + changed['url']).read()
    with wave.open(io.BytesIO(audio)) as wav:
        duration = wav.getnframes() / wav.getframerate()
        assert wav.getframerate() == 48000 and wav.getnchannels() == 1
        assert duration > 0 and abs(duration - result['duration'] / speed) < 0.18, (speed, duration)
    durations[str(speed)] = round(duration, 3)
assert request({'source': '../app.py', 'speed': 1}, route='/tempo')[0] == 400
assert request({'source': result['source'], 'speed': 8}, route='/tempo')[0] == 400
code, fast = request({'text': 'Türkçe metinleri yerel web sitesinde kolayca seslendirebiliriz.', 'speed': 7})
assert code == 200 and fast['speed'] == 7 and fast['duration'] > 0
print(json.dumps({'normal_seconds': result['duration'], 'all_speeds_seconds': durations}, ensure_ascii=False))
print("Üretim, 15 hız, 7x doğrudan üretim, WAV, giriş sınırları ve erişim kontrolleri geçti.")
