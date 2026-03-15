# Esbab-ı Nüzul (Kur'an-ı Kerim İniş Sebepleri)

PyQt5 ile geliştirilmiş, Kur'an-ı Kerim ayetlerini, sûrelerini, cüzlerini ve nüzul (iniş) sebeplerini rahatça okuyup araştırabileceğiniz masaüstü uygulaması.

## Özellikler (Features)
- **Kapsamlı Veri:** 114 Sûre, Ayetler ve Diyanet Meali ile Nüzul Sebepleri.
- **Hızlı Arama:** Sûre, cüz veya sayfa bazlı arama yapma imkanı.
- **Modern Arayüz:** Göz yormayan şık Gece/Gündüz (Dark/Light) modu.
- **Dinamik Metin Boyutu:** Okuma kolaylığı için ayarlanabilir yazı tipi boyutu.
- **Yer İmleri ve Kaynakça:** Kaldığınız yeri kaydetme ve ayetlerin nüzul sebebi kaynaklarını görüntüleme.

## Kurulum ve Kullanım (Installation & Usage)

Programı iki farklı şekilde kullanabilirsiniz: Hızlı Kurulum (Önerilen) veya Kaynak Koddan Çalıştırma.

### Yöntem 1: Tek Tıkla Hızlı Kurulum (Kullanıcılar İçin Önerilen)
Hiçbir teknik bilgiye gerek duymadan, saniyeler içinde programı kullanmaya başlayabilirsiniz:
1. Projenin [Releases (Sürümler)](https://github.com/yilmaz1788/esbabinuzul/releases) sekmesine veya dosyalar arasına gidin.
2. `Esbabi_Nuzul_Kurulum.exe` dosyasını bilgisayarınıza indirin.
3. İndirdiğiniz *.exe* dosyasına çift tıklayın. (Windows uyarı verirse "Yine de çalıştır" seçeneğini seçin).
4. Program herhangi bir ekstra kuruluma (Next-Next vs.) gerek kalmadan, geçici dosyaları çıkarıp anında karşınıza açılacaktır!

### Yöntem 2: Kaynak Koddan Çalıştırma (Geliştiriciler İçin)
Eğer kodları incelemek veya projeyi kendiniz derlemek isterseniz:

#### Gereksinimler
- Python 3.8+
- PyQt5

#### Çalıştırma
1. Repoyu bilgisayarınıza indirin (clone).
2. Gerekli kütüphaneleri kurun:
```bash
pip install -r requirements.txt
```
3. Uygulamayı başlatın:
```bash
python main.py
```

## Derleme (Exe Oluşturma)
Kendi bilgisayarınızda `.exe` dosyası oluşturmak (PyInstaller ile) isterseniz:
```bash
pyinstaller --noconsole --onefile --windowed --add-data "data.json;." --add-data "quran_meta.json;." --name "Esbabi_Nuzul" main.py
```

## Katkıda Bulunma
Her türlü hata bildirimi ve geliştirme önerisi için "Issue" açabilir veya "Pull Request" gönderebilirsiniz.

## Lisans
MIT License
