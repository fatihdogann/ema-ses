"""Bu kurulum için Finder’dan açılabilen EMA Ses.app oluşturur."""
import plistlib
import shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    app = ROOT / 'EMA Ses.app'
    executable = app / 'Contents/MacOS/EMA-Ses'
    executable.parent.mkdir(parents=True, exist_ok=True)
    info = {'CFBundleName': 'EMA Ses', 'CFBundleDisplayName': 'EMA Ses',
            'CFBundleIdentifier': 'local.ema-ses', 'CFBundleVersion': '2',
            'CFBundleShortVersionString': '2.0', 'CFBundlePackageType': 'APPL',
            'CFBundleExecutable': 'EMA-Ses', 'LSUIElement': True}
    (app / 'Contents/Info.plist').write_bytes(plistlib.dumps(info))
    executable.write_text('#!/bin/zsh\nexec ' + shlex.quote(str(ROOT / '.venv/bin/python'))
                          + ' ' + shlex.quote(str(ROOT / 'launch.py')) + '\n')
    executable.chmod(0o755)
    print(f'Hazır: {app}\nFinder’da çift tıklayarak açabilirsin. Kurulum klasörünü taşırsan bu komutu tekrar çalıştır.')


if __name__ == '__main__':
    main()
