import asyncio
from playwright.async_api import async_playwright
import pickle
import os
import csv
from glob import glob
from urllib.parse import urlparse
import json
import random

async def main():
    # Cari file dengan ekstensi .pkl di folder yang sama dengan script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pkl_files = glob(os.path.join(script_dir, "*.pkl"))

    if not pkl_files:
        print("Tidak ditemukan file .pkl di folder yang sama dengan script.")
        return

    # Ambil file cookie pertama yang ditemukan
    cookie_file = pkl_files[0]
    print(f"Menggunakan file cookie: {cookie_file}")

    # Lokasi file status.csv
    status_file = os.path.join(script_dir, "status.csv")
    if not os.path.exists(status_file):
        print("File status.csv tidak ditemukan di folder script.")
        return

    # Baca file status.csv
    with open(status_file, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        rows_to_process = [row for row in reader if not row["Indexed"]]

    if not rows_to_process:
        print("Semua kolom Indexed sudah terisi. Tidak ada link untuk dibuka.")
        return

    print(f"Ditemukan {len(rows_to_process)} baris untuk diproses.")

    async with async_playwright() as p:
        # Pilih browser (bisa 'chromium', 'firefox', atau 'webkit')
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # Muat cookie dari file
        with open(cookie_file, "rb") as f:
            cookies = pickle.load(f)
            await context.add_cookies(cookies)
            print("Cookies loaded successfully.")

        # Buka tab baru
        page = await context.new_page()

        # Proses setiap link di kolom Profile yang Indexed-nya kosong
        for row in rows_to_process:
            original_link = row["Profile"]
            parsed_url = urlparse(original_link)
            username = parsed_url.path.strip("/").split("/")[0]  # Ambil bagian setelah domain dan hilangkan "/"
            api_link = f"https://api.pinterest.com/v3/users/{username}/"  # Buat API link            

            # Gunakan tab yang sama untuk membuka link berikutnya
            await page.goto(api_link)

            # Tunggu hingga halaman selesai dimuat
            await page.wait_for_load_state("domcontentloaded")

            # Ekstrak data JSON dari halaman
            content = await page.evaluate("() => document.body.innerText")
            try:
                # Parse JSON
                json_data = json.loads(content)

                # Cek apakah statusnya "failure"
                if json_data.get("status") == "failure":
                    print(f"Pengguna tidak ditemukan untuk {username}. Menandai sebagai Deactive.")
                    row["Indexed"] = "Deactive"  # Menandai kolom Indexed sebagai "Deactive"
                else:
                    user_data = json_data.get("data", None)
                    
                    if user_data:
                        row["Indexed"] = str(user_data.get("indexed", False)).lower()
                        row["Follower"] = user_data.get("follower_count", 0)
                        row["Following"] = user_data.get("following_count", 0)
                        row["Boards"] = user_data.get("board_count", 0)
                        row["Pins"] = user_data.get("pin_count", 0)
                        row["Views"] = user_data.get("profile_views", 0)
                        print(f"Data untuk {username} diperbarui.")
                    else:
                        print(f"Data untuk {username} tidak ditemukan.")
            except json.JSONDecodeError:
                print(f"Error: Respons dari {api_link} bukan JSON valid.")

            # Tunggu beberapa detik sebelum melanjutkan ke link berikutnya
            await page.wait_for_timeout(random.randint(1000, 2000))

        # Tutup browser setelah selesai memproses semua link
        await browser.close()
        print("Semua link telah diproses. Browser ditutup.")

    # Perbarui file status.csv dengan data terbaru
    with open(status_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = rows_to_process[0].keys()  # Ambil nama kolom dari data
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_to_process)
    print("File status.csv diperbarui dengan nilai terbaru.")

# Jalankan skrip
if __name__ == "__main__":
    asyncio.run(main())