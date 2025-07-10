import signal, sys, pickle, glob, pandas as pd, os
from playwright.sync_api import sync_playwright

base_path = os.path.dirname(os.path.abspath(__file__))
running = True

def save_and_exit(signal, frame):
    global running
    running = False
    print("Script dihentikan, menyimpan CSV...")
    save_csv()
    sys.exit(0)

signal.signal(signal.SIGINT, save_and_exit)

def save_csv():
    try:
        df.to_csv(csv_file, index=False)
    except PermissionError:
        print("\nPERINGATAN: File 'status.csv' sedang terbuka. Tutup file dan coba lagi.\n")
        input("Tekan Enter setelah file 'status.csv' ditutup untuk melanjutkan...")
        save_csv()

csv_file = 'status.csv'
while True:
    try:
        df = pd.read_csv(csv_file)
        break
    except PermissionError:
        print("\nPERINGATAN: File 'status.csv' sedang terbuka. Tutup file dan coba lagi.\n")
        input("Tekan Enter setelah file 'status.csv' ditutup untuk melanjutkan...")

if 'Indexed' not in df.columns:
    df['Indexed'] = ''
df['Indexed'] = df['Indexed'].astype('string')

def load_cookies(page):
    cookie_files = glob.glob("*.pkl")
    if cookie_files:
        with open(cookie_files[0], 'rb') as f:
            cookies = pickle.load(f)
            page.goto("https://pinterest.com/")
            for cookie in cookies:
                if 'domain' in cookie and cookie['domain'] in page.url:
                    page.context.add_cookies([cookie])
        print(f"Cookies berhasil dimuat dari {cookie_files[0]}.")
    else:
        print("Tidak ada file cookies (.pkl) ditemukan di folder.")

def check_shadow_status(page, url, profile_text):
    try:
        page.goto(url)
        page.wait_for_timeout(5000)
        if "show_error=true" in page.url:
            print(f"{url} : Terdeteksi Deactive (?show_error=true)")
            return "Deactive"
        print(f"{url} : Terdeteksi Active")
        pinterest_url = f"https://pinterest.com/search/users/?q={profile_text}&rs=typed"
        page.goto(pinterest_url)
        try:
            xpath = f"//a[contains(@href, '/{profile_text}/')]"
            page.wait_for_selector(xpath, timeout=10000)
            print(f"'/{profile_text}/' Terindex")
            return "True"
        except Exception:
            print(f"{profile_text} Belum Terindex")
            return "False"
        finally:
            page.wait_for_timeout(5000)
    except Exception as e:
        print(f"Error saat mengakses {url}: {e}")
        return "Deactive"

def save_cookies(page):
    cookie_files = glob.glob("*.pkl")
    if cookie_files:
        filename = cookie_files[0]  # Gunakan file yang sudah ada
    else:
        filename = "cookies.pkl"   # Fallback kalau belum ada (jarang terjadi)

    cookies = page.context.cookies()
    with open(filename, "wb") as f:
        pickle.dump(cookies, f)
    print(f"Cookies berhasil diperbarui dan disimpan ke '{filename}'.")


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    load_cookies(page)
    for index, row in df.iterrows():
        if not running:
            break
        profile_url = row['Profile']
        shadow = row['Indexed']
        if pd.notna(shadow) and shadow in ["True", "False", "Deactive"]:
            print(f"Status untuk {profile_url} sudah ada ({shadow}), melewati.")
            continue
        if pd.notna(profile_url):
            print(f"===================================================================")
            print(f"{profile_url} : Sedang di Cek")
            profile_text = profile_url.rstrip('/').split('/')[-1]
            shadow = check_shadow_status(page, profile_url, profile_text)
            df.at[index, 'Indexed'] = shadow
            save_csv()
    print("Selesai, menutup browser...")
    save_cookies(page)
    browser.close()
