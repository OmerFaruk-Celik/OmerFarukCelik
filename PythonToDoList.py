# Görev Yönetim Uygulaması (To-Do List)
import os
import hashlib
from datetime import datetime
import re

# Özel hata sınıfları
class GorevHata(Exception):
    """Görevle ilgili hatalar için özel hata sınıfı"""
    pass

class DosyaHata(Exception):
    """Dosya işlemleriyle ilgili hatalar için özel hata sınıfı"""
    pass

class GirisHata(Exception):
    """Kullanıcı girişleriyle ilgili hatalar için özel hata sınıfı"""
    pass

# Görevleri saklamak için liste (sözlük olarak)
gorevler = []

# Dosya adları
DOSYA_ADI = "tasks.txt"
HASH_DOSYA_ADI = "hash.txt"

# Terminali temizleme fonksiyonu
def terminali_temizle():
    os.system('cls' if os.name == 'nt' else 'clear')

# Görev metninin SHA-256 hash'ini hesaplama
def gorev_hash_hesapla(gorev):
    try:
        return hashlib.sha256(gorev.encode('utf-8')).hexdigest()
    except Exception as e:
        raise GorevHata(f"Hash hesaplama hatası: {e}")

# Hash'in zaten var olup olmadığını kontrol etme
def hash_var_mi(yeni_gorev):
    yeni_hash = gorev_hash_hesapla(yeni_gorev)
    try:
        if os.path.exists(HASH_DOSYA_ADI):
            with open(HASH_DOSYA_ADI, "r", encoding="utf-8") as dosya:
                for satir in dosya:
                    if yeni_hash in satir:
                        return True
        return False
    except Exception as e:
        raise DosyaHata(f"Hash kontrolü sırasında hata: {e}")

# Tarih formatını doğrulama (GG/AA/YYYY)
def tarih_dogrula(tarih):
    pattern = r"^\d{2}/\d{2}/\d{4}$"
    if not re.match(pattern, tarih):
        raise GirisHata("Geçersiz tarih formatı! GG/AA/YYYY formatında girin.")
    try:
        datetime.strptime(tarih, "%d/%m/%Y")
        return True
    except ValueError:
        raise GirisHata("Geçersiz tarih! Lütfen geçerli bir tarih girin.")

# Görevleri dosyadan okuma fonksiyonu
def gorevleri_oku():
    global gorevler
    try:
        if os.path.exists(DOSYA_ADI):
            with open(DOSYA_ADI, "r", encoding="utf-8") as dosya:
                gorevler = []
                for satir in dosya:
                    if satir.strip():
                        try:
                            metin, tarih, oncelik, teslim_tarihi = satir.strip().split("|")
                            if not tarih_dogrula(teslim_tarihi) or not tarih_dogrula(tarih):
                                raise GirisHata("Dosyada geçersiz tarih formatı.")
                            if oncelik not in ["Yüksek", "Orta", "Düşük"]:
                                raise GirisHata("Dosyada geçersiz öncelik seviyesi.")
                            gorevler.append({
                                "metin": metin,
                                "tarih": tarih,
                                "oncelik": oncelik,
                                "teslim_tarihi": teslim_tarihi
                            })
                        except ValueError:
                            raise DosyaHata("Dosya formatı hatalı: Her satır metin|tarih|oncelik|teslim_tarihi içermeli.")
            print("Görevler başarıyla yüklendi.")
            hashleri_guncelle()
        else:
            print("Görev dosyası bulunamadı veya okunamadı. Yeni bir liste oluşturuldu.")
            gorevler = []
    except Exception as e:
        raise DosyaHata(f"Dosya okunurken hata: {e}")

# Hash'leri dosyaya kaydetme fonksiyonu
def hashleri_kaydet():
    try:
        with open(HASH_DOSYA_ADI, "w", encoding="utf-8") as dosya:
            for i, gorev in enumerate(gorevler, 1):
                hash_degeri = gorev_hash_hesapla(gorev["metin"])
                dosya.write(f"{i}: {hash_degeri}\n")
        print("Hash'ler başarıyla kaydedildi.")
    except Exception as e:
        raise DosyaHata(f"Hash dosyası kaydedilirken hata: {e}")

# Görevleri ve hash'leri dosyaya kaydetme
def gorevleri_kaydet():
    try:
        with open(DOSYA_ADI, "w", encoding="utf-8") as dosya:
            for gorev in gorevler:
                dosya.write(f"{gorev['metin']}|{gorev['tarih']}|{gorev['oncelik']}|{gorev['teslim_tarihi']}\n")
        print("Görevler başarıyla kaydedildi.")
        hashleri_kaydet()
    except Exception as e:
        raise DosyaHata(f"Dosya kaydedilirken hata: {e}")

# Hash'leri güncelleme (görevler değiştiğinde)
def hashleri_guncelle():
    if gorevler:
        hashleri_kaydet()
    else:
        try:
            with open(HASH_DOSYA_ADI, "w", encoding="utf-8") as dosya:
                dosya.write("")
        except Exception as e:
            raise DosyaHata(f"Hash dosyası temizlenirken hata: {e}")

# Görevleri listeleme fonksiyonu
def gorevleri_listele():
    if not gorevler:
        print("Henüz görev bulunmamaktadır.")
    else:
        print("\n--- GÖREV LİSTESİ ---")
        for i, gorev in enumerate(gorevler, 1):
            print(f"{i}. {gorev['metin']} (Öncelik: {gorev['oncelik']}, Ekleme Tarihi: {gorev['tarih']}, Teslim: {gorev['teslim_tarihi']})")
        print("--------------------")
        try:
            if os.path.exists(HASH_DOSYA_ADI):
                with open(HASH_DOSYA_ADI, "r", encoding="utf-8") as dosya:
                    print("\n--- GÖREV HASH'LERİ ---")
                    print(dosya.read().strip())
                    print("--------------------")
        except Exception as e:
            raise DosyaHata(f"Hash dosyası okunurken hata: {e}")

# Yeni görev ekleme fonksiyonu
def yeni_gorev_ekle():
    try:
        gorev = input("Yeni görev: ").strip()
        if not gorev:
            raise GorevHata("Boş görev eklenemez!")
        if hash_var_mi(gorev):
            raise GorevHata(f"'{gorev}' zaten listede mevcut!")
        
        # Öncelik seçimi
        print("Öncelik seviyesi seçin (1: Yüksek, 2: Orta, 3: Düşük)")
        oncelik_secim = input("Seçiminiz (1-3): ")
        if oncelik_secim == "1":
            oncelik = "Yüksek"
        elif oncelik_secim == "2":
            oncelik = "Orta"
        elif oncelik_secim == "3":
            oncelik = "Düşük"
        else:
            raise GirisHata("Geçersiz öncelik seçimi! Lütfen 1-3 arasında bir sayı girin.")
        
        # Teslim tarihi
        teslim_tarihi = input("Teslim tarihi (GG/AA/YYYY): ").strip()
        tarih_dogrula(teslim_tarihi)
        
        # Ekleme tarihi (otomatik)
        ekleme_tarihi = datetime.now().strftime("%d/%m/%Y")
        
        gorevler.append({
            "metin": gorev,
            "tarih": ekleme_tarihi,
            "oncelik": oncelik,
            "teslim_tarihi": teslim_tarihi
        })
        print(f"'{gorev}' görevi eklendi.")
        gorevleri_kaydet()
    except (GorevHata, GirisHata, DosyaHata) as e:
        print(f"Hata: {e}")

# Görev düzenleme fonksiyonu
def gorev_duzenle():
    gorevleri_listele()
    if not gorevler:
        return
    try:
        secim = input("Düzenlemek istediğiniz görevin numarası: ")
        secim = int(secim) - 1
        if not 0 <= secim < len(gorevler):
            raise GirisHata("Geçersiz görev numarası!")
        
        yeni_metin = input(f"Yeni görev metni ({gorevler[secim]['metin']}): ").strip()
        if not yeni_metin:
            raise GorevHata("Boş görev eklenemez!")
        if hash_var_mi(yeni_metin) and yeni_metin != gorevler[secim]["metin"]:
            raise GorevHata(f"'{yeni_metin}' zaten listede mevcut!")
        
        # Yeni öncelik
        print("Yeni öncelik seviyesi seçin (1: Yüksek, 2: Orta, 3: Düşük)")
        oncelik_secim = input("Seçiminiz (1-3): ")
        if oncelik_secim == "1":
            oncelik = "Yüksek"
        elif oncelik_secim == "2":
            oncelik = "Orta"
        elif oncelik_secim == "3":
            oncelik = "Düşük"
        else:
            raise GirisHata("Geçersiz öncelik seçimi! Lütfen 1-3 arasında bir sayı girin.")
        
        # Yeni teslim tarihi
        teslim_tarihi = input(f"Yeni teslim tarihi ({gorevler[secim]['teslim_tarihi']}): ").strip()
        tarih_dogrula(teslim_tarihi)
        
        gorevler[secim]["metin"] = yeni_metin
        gorevler[secim]["oncelik"] = oncelik
        gorevler[secim]["teslim_tarihi"] = teslim_tarihi
        print("Görev başarıyla güncellendi.")
        gorevleri_kaydet()
    except ValueError:
        print("Hata: Lütfen bir sayı girin!")
    except (GorevHata, GirisHata, DosyaHata) as e:
        print(f"Hata: {e}")

# Görev silme fonksiyonu
def gorev_sil():
    gorevleri_listele()
    if not gorevler:
        return
    try:
        secim = input("Silmek istediğiniz görevin numarası: ")
        secim = int(secim) - 1
        if not 0 <= secim < len(gorevler):
            raise GirisHata("Geçersiz görev numarası!")
        silinen = gorevler.pop(secim)
        print(f"'{silinen['metin']}' görevi silindi.")
        gorevleri_kaydet()
    except ValueError:
        print("Hata: Lütfen bir sayı girin!")
    except GirisHata as e:
        print(f"Hata: {e}")

# Ana menü fonksiyonu
def ana_menu():
    try:
        gorevleri_oku()
    except DosyaHata as e:
        print(f"Hata: {e}")
        return
    while True:
        terminali_temizle()
        print("\n--- TO-DO LIST UYGULAMASI ---")
        print("1. Görevleri Listele")
        print("2. Yeni Görev Ekle")
        print("3. Görev Düzenle")
        print("4. Görev Sil")
        print("5. Çıkış")
        
        secim = input("Seçiminiz (1-5): ")
        
        try:
            if secim == "1":
                gorevleri_listele()
            elif secim == "2":
                yeni_gorev_ekle()
            elif secim == "3":
                gorev_duzenle()
            elif secim == "4":
                gorev_sil()
            elif secim == "5":
                print("Programdan çıkılıyor...")
                break
            else:
                raise GirisHata("Geçersiz seçim! Lütfen 1-5 arasında bir sayı girin.")
            input("Ana menü için 'Enter' basınız")
        except GirisHata as e:
            print(f"Hata: {e}")
            input("Ana menü için 'Enter' basınız")

# Programı başlat
if __name__ == "__main__":
    print("To-Do List Uygulamasına Hoş Geldiniz!")
    ana_menu()
