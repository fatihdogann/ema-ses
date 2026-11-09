"""Klasöründeki başlatıcıyı açan taşınabilir EMA Ses.app oluşturur."""
import plistlib
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
    executable.write_text(
        '#!/bin/zsh\n'
        'launcher="${0:A:h:h:h:h}/Baslat.command"\n'
        'if [[ "$1" == "--no-browser" ]]; then exec "$launcher" "$@"; fi\n'
        'exec /usr/bin/open -a Terminal "$launcher"\n',
        encoding='utf-8',
    )
    executable.chmod(0o755)
    print(f'Hazır: {app}\nUygulamayı açmak için klasörü bir arada tut ve Finder’dan çift tıkla.')


if __name__ == '__main__':
    main()
