"""Kaynakları kendi içinde taşıyan bir macOS uygulaması oluşturur."""
import plistlib
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    destination = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT
    uv = shutil.which('uv')
    if uv is None:
        sys.exit('EMA Ses.app oluşturmak için önce uv kur.')
    app = destination / 'EMA Ses.app'
    executable = app / 'Contents/MacOS/EMA-Ses'
    executable.parent.mkdir(parents=True, exist_ok=True)
    resources = app / 'Contents/Resources'
    resources.mkdir(exist_ok=True)
    for name in ('app.py', 'index.html', 'launch.py', 'pyproject.toml', 'uv.lock', 'Baslat.command', 'LICENSE'):
        shutil.copy2(ROOT / name, resources / name)
    shutil.copy2(uv, resources / 'uv')
    info = {'CFBundleName': 'EMA Ses', 'CFBundleDisplayName': 'EMA Ses',
            'CFBundleIdentifier': 'local.ema-ses', 'CFBundleVersion': '2',
            'CFBundleShortVersionString': '2.0', 'CFBundlePackageType': 'APPL',
            'CFBundleExecutable': 'EMA-Ses', 'LSUIElement': True}
    (app / 'Contents/Info.plist').write_bytes(plistlib.dumps(info))
    executable.write_text(
        '#!/bin/zsh\n'
        'runtime="${EMA_RUNTIME_DIR:-$HOME/Library/Application Support/EMA Ses}"\n'
        'if ! /bin/mkdir -p "$runtime" || ! /usr/bin/rsync -rtp "${0:A:h:h}/Resources/" "$runtime/"; then\n'
        '  if [[ "$1" != "--no-browser" ]]; then\n'
        '    /usr/bin/osascript -e \'display alert "EMA Ses açılamadı" message "Uygulama dosyaları kullanıcı klasörüne yazılamadı."\'\n'
        '  fi\n'
        '  exit 1\n'
        'fi\n'
        'launcher="$runtime/Baslat.command"\n'
        'if [[ "$1" == "--no-browser" ]]; then exec "$launcher" "$@"; fi\n'
        'exec /usr/bin/open -a Terminal "$launcher"\n',
        encoding='utf-8',
    )
    executable.chmod(0o755)
    print(f'Hazır: {app}\nUygulamayı açmak için Finder’dan çift tıkla.')


if __name__ == '__main__':
    main()
