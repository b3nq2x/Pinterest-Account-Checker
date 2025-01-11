import signal
import sys
import pickle
import glob
import pandas as pd
import os
from playwright.sync_api import sync_playwright

# Menentukan path relatif
base_path = os.path.dirname(os.path.abspath(__file__))  # Mengambil path dari file script saat ini

# Variabel untuk menandai apakah script sedang berjalan
running = True

# Fungsi untuk menyimpan CSV ketika script dihentikan
def save_and_exit(signal, frame):
    global running
    running = False
    print("Script dihentikan, menyimpan CSV...")
    save_csv()
    sys.exit(0)

# Tangkap sinyal Ctrl+C
signal.signal(signal.SIGINT, save_and_exit)

# Fungsi untuk menyimpan CSV dengan penanganan file terbuka
def save_csv():
    try:
        df.to_csv(csv_file, index=False)
    except PermissionError:
        print("\nPERINGATAN: File 'status.csv' sedang terbuka. Tutup file dan coba lagi.\n")
        input("Tekan Enter setelah file 'status.csv' ditutup untuk melanjutkan...")
        save_csv()

# Baca file CSV dengan penanganan file terbuka
csv_file = 'status.csv'
while True:
    try:
        df = pd.read_csv(csv_file)
        break
    except PermissionError:
        print("\nPERINGATAN: File 'status.csv' sedang terbuka. Tutup file dan coba lagi.\n")
        input("Tekan Enter setelah file 'status.csv' ditutup untuk melanjutkan...")

# Pastikan kolom 'Indexed' bertipe string
if 'Indexed' not in df.columns:
    df['Indexed'] = ''  # Inisialisasi sebagai string kosong

df['Indexed'] = df['Indexed'].astype('string')

# Fungsi untuk memuat cookies dari file .pkl
def load_cookies(page):
    cookie_files = glob.glob("*.pkl")
    if cookie_files:
        cookie_file = cookie_files[0]
        with open(cookie_file, 'rb') as f:
            cookies = pickle.load(f)
            page.goto("https://id.pinterest.com/")  # Ganti dengan URL yang sesuai untuk login
            for cookie in cookies:
                if 'domain' in cookie and cookie['domain'] in page.url:
                    page.context.add_cookies([cookie])
        print(f"Cookies berhasil dimuat dari {cookie_file}.")
    else:
        print("Tidak ada file cookies (.pkl) ditemukan di folder.")

# Fungsi untuk mengecek status profile menggunakan Playwright
def check_shadow_status(page, url, profile_text):
    try:
        page.goto(url)
        page.wait_for_timeout(5000)

        if "show_error=true" in page.url:
            print(f"{url} : Terdeteksi Deactive (?show_error=true)")
            return "Deactive"

        print(f"{url} : Terdeteksi Active")

        pinterest_url = f"https://id.pinterest.com/search/users/?q={profile_text}&rs=typed"
        page.goto(pinterest_url)

        try:
            xpath = f"//a[contains(@href, '/{profile_text}/')]"
            element = page.wait_for_selector(xpath, timeout=10000)            
            print(f"'/{profile_text}/' Terindex")
            shadow_status = "True"
        except Exception:
            print(f"{profile_text} Belum Terindex")
            shadow_status = "False"

        page.wait_for_timeout(5000)
        return shadow_status

    except Exception as e:
        print(f"Error saat mengakses {url}: {e}")
        return "Deactive"

# Fungsi utama untuk menjalankan proses menggunakan Playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # Load cookies
    load_cookies(page)

    # Loop melalui setiap baris dalam CSV
    for index, row in df.iterrows():
        if not running:  # Jika script dihentikan, keluar dari loop
            break

        profile_url = row['Profile']
        shadow = row['Indexed']

        # Lewati pengecekan jika shadow status sudah ada
        if pd.notna(shadow) and shadow in ["True", "False", "Deactive"]:
            print(f"Status untuk {profile_url} sudah ada ({shadow}), melewati.")
            continue

        if pd.notna(profile_url):  # Cek jika URL tidak kosong
            print(f"===================================================================")
            print(f"{profile_url} : Sedang di Cek")

            # Ekstrak bagian username dari URL
            profile_text = profile_url.rstrip('/').split('/')[-1]
            shadow = check_shadow_status(page, profile_url, profile_text)

            # Perbarui dataframe dengan nilai yang baru
            df.at[index, 'Indexed'] = shadow

            # Simpan ke file CSV setiap kali setelah diperbarui
            save_csv()

    # Tutup browser setelah selesai
    print("Selesai, menutup browser...")
    browser.close()
