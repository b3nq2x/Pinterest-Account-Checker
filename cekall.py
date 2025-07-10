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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pkl_files = glob(os.path.join(script_dir, "*.pkl"))

    if not pkl_files:
        print("Tidak ditemukan file .pkl di folder yang sama dengan script.")
        return

    cookie_file = pkl_files[0]
    print(f"Menggunakan file cookie: {cookie_file}")

    status_file = os.path.join(script_dir, "status.csv")
    if not os.path.exists(status_file):
        print("File status.csv tidak ditemukan di folder script.")
        return

    with open(status_file, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    rows_to_process = [row for row in rows if not row["Indexed"]]

    if not rows_to_process:
        print("Semua kolom Indexed sudah terisi. Tidak ada link untuk dibuka.")
        return

    print(f"Ditemukan {len(rows_to_process)} baris untuk diproses.")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # Load cookies
        with open(cookie_file, "rb") as f:
            cookies = pickle.load(f)
            await context.add_cookies(cookies)
            print("Cookies loaded successfully.")

        # Tab 1: Cek login di pinterest.com
        page1 = await context.new_page()
        await page1.goto("https://www.pinterest.com/")
        await page1.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(2)

        # Verifikasi login
        page_title = await page1.title()
        if "Login" in page_title or "Sign up" in page_title:
            print("Login gagal. Cookie tidak valid atau kadaluarsa.")
            await browser.close()
            return
        else:
            print("Login berhasil. Melanjutkan ke pengecekan akun...")

        # Tab 2: Proses API pengecekan akun
        page2 = await context.new_page()

        for row in rows_to_process:
            original_link = row["Profile"]
            parsed_url = urlparse(original_link)
            username = parsed_url.path.strip("/").split("/")[0]
            api_link = f"https://api.pinterest.com/v3/users/{username}/"

            await page2.goto(api_link)
            await page2.wait_for_load_state("domcontentloaded")

            content = await page2.evaluate("() => document.body.innerText")

            try:
                json_data = json.loads(content)

                if json_data.get("status") == "failure":
                    print(f"{username} : Deactive")
                    row["Indexed"] = "Suspended"
                else:
                    user_data = json_data.get("data", None)
                    if user_data:
                        if user_data.get("seo_noindex_reason") == "user_spam":
                            print(f"{username} : Shadow Ban")
                            row["Indexed"] = "Shadow Ban"
                        else:
                            print(f"{username} : Active")
                            row["Indexed"] = str(user_data.get("indexed", False)).lower()

                        row["Follower"] = user_data.get("follower_count", 0)
                        row["Following"] = user_data.get("following_count", 0)
                        row["Boards"] = user_data.get("board_count", 0)
                        row["Pins"] = user_data.get("pin_count", 0)
                        row["Views"] = user_data.get("profile_views", 0)
                    else:
                        print(f"Data untuk {username} tidak ditemukan.")
            except json.JSONDecodeError:
                print(f"Error: Respons dari {api_link} bukan JSON valid.")

            await page2.wait_for_timeout(random.randint(1000, 2000))

        await browser.close()
        print("Semua link telah diproses. Browser ditutup.")

    # Update status.csv
    with open(status_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = rows[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("File status.csv diperbarui dengan nilai terbaru.")

if __name__ == "__main__":
    asyncio.run(main())
#hello