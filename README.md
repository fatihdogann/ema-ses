# EMA Ses

Türkçe metinleri sese dönüştüren, sesleri tarayıcıdan dinleyip WAV olarak indirebildiğin yerel web uygulaması.

[EMA Lightning](https://huggingface.co/canberkkkkkk/ema-lightning) modelini kullanır. Modelin geliştiricisi **Canberk Aslan**; bu depo, modelin çevresindeki kullanım ekranını ve macOS başlatıcısını içerir.

## Özellikler

- **Metinden ses:** Türkçe metni yaz, üret, oynatıcıdan dinle, istersen WAV indir.
- **15 hız seçeneği:** 0.75x, 0.9x, 1x, 1.25x, 2x, 2.5x, 3x, 3.5x, 4x, 4.5x, 5x, 5.5x, 6x, 6.5x ve 7x.
- **Üretim sonrası hız değişimi:** Tekrar ses üretmeden hızı değiştir; oynatıcı ve indirilen dosya birlikte güncellenir.
- **Açık/koyu tema:** Sistem temasını izler, seçtiğin temayı tarayıcıda hatırlar.
- **macOS uygulaması:** Finder’dan çift tıklayınca sunucu arka planda hazırlanır ve site açılır.
- **Yerel çalışma:** İlk model indirmesinden sonra ses üretimi çevrimdışı yapılır; API anahtarı gerekmez.
- **Telefon görünümü:** Tailscale Serve ile kendi özel ağından erişebilirsin.

## Kullanılan teknolojiler

Python 3.11–3.13, standart kütüphane HTTP sunucusu, HTML/CSS/JavaScript, PyTorch, EMA Lightning 1.0.1 ve FFmpeg. Tailscale isteğe bağlıdır. Bu kurulum macOS için hazırlanmıştır.

## Kurulum

[Homebrew](https://brew.sh/) ve [Git](https://git-scm.com/) kurulu olmalıdır.

```sh
brew install uv ffmpeg
git clone https://github.com/fatihdogann/ema-ses.git
cd ema-ses
uv venv --python 3.13
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python uygulama_olustur.py
```

Oluşan **EMA Ses.app** dosyasına çift tıkla. İlk açılışta model ağırlıkları indirilir ve model hazırlanır; ardından tarayıcı açılır. Sonraki açılışlarda model dosyaları önbellekten kullanılır. Kurulum klasörünü taşırsan `uygulama_olustur.py` komutunu tekrar çalıştır.

İstersen aynı ekrana `Baslat.command` dosyasıyla da ulaşabilirsin.

## Kullanım

1. EMA Ses uygulamasını aç.
2. Metnini yaz; dinleme ve indirme hızını seç.
3. **Ses üret** düğmesine bas.
4. Oynatıcıdan dinle veya **WAV dosyasını indir** bağlantısını kullan.
5. Sonradan hızı değiştirebilirsin. Çıkarken **Uygulamayı kapat** düğmesine bas.

Yerel adres: `http://127.0.0.1:7868`. Sesler `sesler/` klasörüne kaydedilir. Tarayıcı sekmesini kapatmak uygulamayı durdurmaz.

## Tailscale ile telefondan erişim

Mac ve telefon aynı Tailscale ağına bağlıyken, EMA Ses’i açıp Mac’te şu komutu çalıştır:

```sh
tailscale serve --bg --https=8443 http://127.0.0.1:7868
```

macOS uygulamasının CLI’ı PATH üzerinde değilse `tailscale` yerine `/Applications/Tailscale.app/Contents/MacOS/Tailscale` kullan. Komutun verdiği HTTPS adresini telefondaki tarayıcıda aç. Mac açık ve uyanık, EMA Ses çalışıyor olmalıdır.

Bu paylaşım Tailscale ağındaki erişim kurallarına tabidir. Proxy’yi kapatmak için:

```sh
tailscale serve --https=8443 off
```

## Doğrulama

Uygulama açıkken:

```sh
.venv/bin/python kontrol.py
```

Kontrol; ses üretimini, 15 hızın sürelerini, 48 kHz mono WAV dosyalarını, HTTP Range/HEAD ve indirme yanıtlarını, giriş sınırlarını ve oturum anahtarını sınar.

M4 / 16 GB macOS kurulumunda Finder çift tıkla açılış, yeniden başlatma sonrası eski sekmeden üretim, tarayıcı oynatımı, hız değişimi, WAV indirme, açık/koyu tema ve Tailscale HTTPS üzerinden üretim doğrulandı. Telefon genişliğinde görünüm test edildi; fiziksel iPhone kabulü ayrıca yapılmalıdır. Bu ölçümler ve kontroller tüm cihazlarda aynı performansı garanti etmez.

## Sınırlar

- Türkçe, tek sabit ses. Ses klonlama ve duygu seçimi yoktur.
- Tek üretimde en fazla 10.000 karakter; daha uzun metinleri bölerek kullan.
- Normal hızdaki ses üretilir; hız seçenekleri FFmpeg tempo dönüşümüyle uygulanır. Sesin perdesi korunur, yüksek hızlarda anlaşılabilirlik azalabilir.
- Sunucu `127.0.0.1` üzerinde çalışır. Telefondan erişim için Tailscale gibi bir özel ağ proxy’si gerekir.
- Ses yapay zekâ ile üretilir. Sonucu yayımlarken bunu belirt; önemli metinlerde telaffuzu dinleyerek kontrol et.

## Model ve lisans

Bu uygulamanın kodu [MIT](LICENSE) lisanslıdır. EMA Lightning kodu ve model ağırlıkları **Apache 2.0** lisanslıdır; bu depoya model ağırlıkları dahil edilmez. İlk açılışta Hugging Face üzerinden indirilir.

- [EMA Lightning modeli](https://huggingface.co/canberkkkkkk/ema-lightning)
- [EMA Lightning kaynak kodu](https://github.com/canberk7/ema-lightning)
- [Python paketi](https://pypi.org/project/ema-lightning/)
- [FFmpeg tempo filtresi](https://ffmpeg.org/ffmpeg-filters.html#atempo)
- [Tailscale Serve](https://tailscale.com/docs/features/tailscale-serve)

---

## İletişim

**Mehmet Fatih Doğan** — backend geliştirici, güvenlik meraklısı.

- 🌐 Portfolyo & iletişim: [mehmetfatihdogan.com.tr](https://mehmetfatihdogan.com.tr)
- 💻 GitHub: [@fatihdogann](https://github.com/fatihdogann)

Proje hakkında soru, hata bildirimi veya geri bildirim için [iletişim sayfamdan](https://mehmetfatihdogan.com.tr/iletisim) ulaşabilirsin.
